from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from itertools import groupby
from typing import Iterable

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpModel, IntVar

from shift.domain.base import Model
from shift.domain.model import EmployeeSlot, get_key
from shift.domain.shift import (
    Day,
    DayAndEvening,
    Period,
    Shift,
    Slot,
    WeekDay,
    consecutive_shifts,
    shift_range,
)


@dataclass
class Planning(Model):
    first_day: date
    last_day: date
    periods: Iterable[Period]
    shift_duration: int
    employees_per_shift: int
    employee_ids: list[int] = field(default_factory=list)
    constraints: list[ModelConstraint] = field(default_factory=list)

    def get_slots(self) -> Iterable[Slot]:
        first_shift = Shift(min(self.periods), Day(self.first_day))
        last_shift = Shift(max(self.periods), Day(self.last_day))

        for shift in shift_range(
            first_shift, last_shift, periods=self.periods, inclusive=True
        ):
            yield Slot(
                period=shift.period,
                day=shift.day,
                duration=self.shift_duration,
                n_employees=self.employees_per_shift,
            )


@dataclass
class ModelConstraint(Model):
    employee_ids: list[int] = field(default_factory=list)

    def add_constraint(
        self,
        slots: Iterable[Slot],
        model: cp_model.CpModel,
        employee_slots: dict[EmployeeSlot, cp_model.IntVar],
    ) -> None:
        raise NotImplementedError


@dataclass
class WorkersPerShift(ModelConstraint):
    def add_constraint(
        self,
        slots: Iterable[Slot],
        model: CpModel,
        employee_slots: dict[EmployeeSlot, cp_model.IntVar],
    ) -> None:
        for slot in slots:
            _sum = sum(
                employee_slots[get_key(employee_id, slot.shift)]
                for employee_id in self.employee_ids
            )
            model.Add(_sum == slot.n_employees)


@dataclass
class ShiftsPerDay(ModelConstraint):
    n: int = 1

    def add_constraint(
        self,
        slots: Iterable[Slot],
        model: CpModel,
        employee_slots: dict[EmployeeSlot, cp_model.IntVar],
    ) -> None:
        if self.n != 1:
            raise

        for day, _slots in groupby(slots, key=lambda slot: slot.day):
            for employee_id in self.employee_ids:
                model.AddAtMostOne(
                    employee_slots[get_key(employee_id, _slot.shift)]
                    for _slot in _slots
                )


@dataclass
class SpecificShifts(ModelConstraint):
    blocked: bool = True

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
            )
            if self.blocked:
                model.Add(sum(_employee_slots) <= 0)
            else:
                for _employee_slot in _employee_slots:
                    model.AddExactlyOne(_employee_slot)


@dataclass
class MaxConsecutiveShifts(ModelConstraint):
    week_days: list[WeekDay] = [1, 2, 3, 4, 5, 6, 7]
    periods: list[Period] = [period for period in DayAndEvening]
    max: int = 1
    window: int = 2

    def add_constraint(
        self,
        slots: Iterable[Slot],
        model: CpModel,
        employee_slots: dict[EmployeeSlot, IntVar],
    ) -> None:
        for _slots in consecutive_shifts(
            self.week_days,
            filter(lambda slot: slot.period in self.periods, slots),
            self.window,
        ):
            for employee_id in self.employee_ids:
                _employee_slots = (
                    employee_slots[get_key(employee_id, slot.shift)]
                    for slot in _slots
                )
                model.Add(sum(_employee_slots) <= self.max)


@dataclass
class MaxRecurrentShifts(ModelConstraint):
    week_days: list[WeekDay] = [6, 7]
    periods: list[Period] = [period for period in DayAndEvening]
    max: int = 1

    def add_constraint(
        self,
        slots: Iterable[Slot],
        model: CpModel,
        employee_slots: dict[EmployeeSlot, IntVar],
    ) -> None:
        slots_per_week = groupby(slots, lambda slot: slot.day.week_number)
        _, _slots_0 = next(slots_per_week)
        _, _slots_1 = next(slots_per_week)
        slots_0 = list(_slots_0)
        slots_1 = list(_slots_1)

        n_weeks = set(
            (slot.day.week_number, slot.day.iso_year) for slot in slots
        )

        for _ in range(len(n_weeks) - 2):
            for employee_id in self.employee_ids:
                _sum = sum(
                    employee_slots[get_key(employee_id, slot.shift)]
                    for slot in filter(
                        lambda _slot: _slot.day.week_day in self.week_days,
                        slots_0 + slots_1,
                    )
                )
                model.Add(_sum <= self.max)

            slots_0 = slots_1
            _, _slots_1 = next(slots_per_week)
            slots_1 = list(_slots_1)
