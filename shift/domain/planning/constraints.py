from __future__ import annotations

import logging
from dataclasses import dataclass, field
from itertools import groupby
from typing import (
    Iterable,
    Iterator,
    Optional,
    Protocol,
    Sequence,
)

from ortools.sat.python import cp_model  # type: ignore
from ortools.sat.python.cp_model import CpModel, IntVar  # type: ignore

from shift.domain.shifts.days import WeekDay, WeekDays
from shift.domain.shifts.periods import DayAndEvening  # type: ignore
from shift.domain.shifts.shift import (
    Period,
    Shift,
    Slot,
    get_consecutive_shifts,
)
from shift.domain.utils.model import Model
from shift.domain.utils.utils import EmployeeSlot, get_key


@dataclass
class Constraints(Model):
    employee_ids: list[int] = field(default_factory=list)
    workers_per_shift: Optional[WorkersPerShift] = field(init=False)
    shifts_per_day: Optional[ShiftsPerDay] = field(init=False)
    specific_shifts: list[SpecificShifts] = field(
        init=False, default_factory=list
    )
    max_consecutive_shifts: list[MaxConsecutiveShifts] = field(
        init=False, default_factory=list
    )
    max_recurrent_shifts: list[MaxRecurrentShifts] = field(
        init=False, default_factory=list
    )

    def add(
        self,
        constraint: PlanningConstraint,
        employee_ids: Optional[list[int]] = None,
    ) -> None:
        if employee_ids:
            constraint.employee_ids = employee_ids
        else:
            constraint.employee_ids = self.employee_ids

        if isinstance(constraint, WorkersPerShift):
            if not getattr(self, "workers_per_shift", None):
                logging.warning(
                    "Replacing existing workers per shift constraint"
                )
            self.workers_per_shift = constraint
        elif isinstance(constraint, ShiftsPerDay):
            if not getattr(self, "shifts_per_day", None):
                logging.warning("Replacing existing shifts per day constraint")
            self.shifts_per_day = constraint
        elif isinstance(constraint, SpecificShifts):
            self.specific_shifts.append(constraint)
        elif isinstance(constraint, MaxConsecutiveShifts):
            self.max_consecutive_shifts.append(constraint)
        elif isinstance(constraint, MaxRecurrentShifts):
            self.max_recurrent_shifts.append(constraint)

    def __iter__(self) -> Iterator[PlanningConstraint]:
        if self.workers_per_shift:
            yield self.workers_per_shift
        if self.shifts_per_day:
            yield self.shifts_per_day
        yield from self.specific_shifts
        yield from self.max_consecutive_shifts
        yield from self.max_recurrent_shifts


class PlanningConstraint(Protocol):
    employee_ids: list[int] = field(init=False)

    def add_constraint(
        self,
        slots: Iterable[Slot],
        model: cp_model.CpModel,
        employee_slots: dict[
            EmployeeSlot,
            cp_model.IntVar,
        ],
    ) -> None:
        ...


@dataclass
class WorkersPerShift(Model):
    employee_ids: list[int] = field(init=False)

    def add_constraint(
        self,
        slots: Iterable[Slot],
        model: CpModel,
        employee_slots: dict[
            EmployeeSlot,
            cp_model.IntVar,
        ],
    ) -> None:
        for slot in slots:
            _sum = sum(
                (
                    employee_slots[get_key(employee_id, slot.shift)]
                    for employee_id in self.employee_ids
                )
            )
            model.Add(_sum == slot.n_employees)


@dataclass
class ShiftsPerDay(Model):
    employee_ids: list[int] = field(init=False)
    n: int = 1

    def add_constraint(
        self,
        slots: Iterable[Slot],
        model: CpModel,
        employee_slots: dict[
            EmployeeSlot,
            cp_model.IntVar,
        ],
    ) -> None:
        if self.n != 1:
            raise

        for day, _slots in groupby(
            slots,
            key=lambda slot: slot.day,
        ):
            for employee_id in self.employee_ids:
                model.AddAtMostOne(
                    employee_slots[get_key(employee_id, _slot.shift)]
                    for _slot in _slots
                )


@dataclass
class SpecificShifts(PlanningConstraint):
    employee_ids: list[int] = field(init=False)
    blocked: bool = True
    shifts: list[Shift] = field(default_factory=list)

    def add_constraint(
        self,
        slots: Iterable[Slot],
        model: CpModel,
        employee_slots: dict[EmployeeSlot, IntVar],
    ) -> None:
        for employee_id in self.employee_ids:
            _employee_slots = (
                employee_slots[get_key(employee_id, slot.shift)]
                for slot in slots
                if slot.shift in self.shifts
            )
            if self.blocked:
                model.Add(sum(_employee_slots) <= 0)
            else:
                for _employee_slot in _employee_slots:
                    model.AddExactlyOne(_employee_slot)


@dataclass
class MaxConsecutiveShifts(PlanningConstraint):
    employee_ids: list[int] = field(init=False)
    week_days: Sequence[WeekDay] = field(default_factory=lambda: WeekDays)
    periods: list[Period] = field(
        default_factory=lambda: [period for period in DayAndEvening]
    )
    max: int = 1
    window: int = 2

    def add_constraint(
        self,
        slots: Iterable[Slot],
        model: CpModel,
        employee_slots: dict[EmployeeSlot, IntVar],
    ) -> None:
        for _slots in get_consecutive_shifts(
            filter(
                lambda slot: slot.period in self.periods,
                slots,
            ),
            self.week_days,
            self.window,
        ):
            for employee_id in self.employee_ids:
                _employee_slots = (
                    employee_slots[get_key(employee_id, slot.shift)]
                    for slot in _slots
                )
                model.Add(sum(_employee_slots) <= self.max)


@dataclass
class MaxRecurrentShifts(PlanningConstraint):
    employee_ids: list[int] = field(init=False)
    week_days: list[WeekDay] = field(default_factory=lambda: [6, 7])
    periods: list[Period] = field(
        default_factory=lambda: [period for period in DayAndEvening]
    )
    max: int = 1

    @property
    def window(self) -> int:
        return 2

    def add_constraint(
        self,
        slots: Iterable[Slot],
        model: CpModel,
        employee_slots: dict[EmployeeSlot, IntVar],
    ) -> None:
        sorted_slots = sorted(slots)
        # groupby week_number (without years
        # because groupby is not actually group.by)
        slots_per_week = groupby(
            sorted_slots, lambda slot: slot.day.week_number
        )

        # retrieve slots from first week
        _, _slots_0 = next(slots_per_week)
        slots_0 = list(_slots_0)

        n_weeks = set(
            (slot.day.week_number, slot.day.iso_year) for slot in sorted_slots
        )

        for _ in range(len(n_weeks) - 1):
            # roll over slots
            slots_1 = slots_0
            _, _slots_0 = next(slots_per_week)
            slots_0 = list(_slots_0)

            for employee_id in self.employee_ids:
                _sum = sum(
                    employee_slots[get_key(employee_id, slot.shift)]
                    for slot in filter(
                        lambda _slot: _slot.day.week_day in self.week_days,
                        slots_0 + slots_1,
                    )
                )
                model.Add(_sum <= self.max)
