from abc import abstractmethod
from dataclasses import dataclass, field
from itertools import groupby
from math import ceil, floor
from typing import Any, Sequence

from ortools.sat.python import cp_model  # type: ignore

from shift.domain.base import Model
from shift.domain.model import EmployeeSlot, get_key
from shift.domain.shift import Slot


@dataclass
class PlanningDistribution(Model):
    employee_hours: dict[int, int] = field(default_factory=dict)

    @abstractmethod
    def add_distribution(
        self,
        slots: Sequence[Slot],
        model: cp_model.CpModel,
        employee_slots: dict[EmployeeSlot, cp_model.IntVar],
    ) -> None:
        raise NotImplementedError

    @property
    def total_hours(self) -> int:
        return sum(self.employee_hours.values())


@dataclass
class NShifts(PlanningDistribution):
    offset: int = 0

    def add_distribution(
        self,
        slots: Sequence[Slot],
        model: cp_model.CpModel,
        employee_slots: dict[EmployeeSlot, Any],
    ) -> None:
        _distribute_slots(
            slots,
            model,
            employee_slots,
            self.employee_hours,
            self.total_hours,
            self.offset,
        )


@dataclass
class NShiftsMonth(PlanningDistribution):
    offset: int = 0

    def add_distribution(
        self,
        slots: Sequence[Slot],
        model: cp_model.CpModel,
        employee_slots: dict[EmployeeSlot, Any],
    ) -> None:
        for month, _slots in groupby(slots, lambda slot: slot.day.month):
            _distribute_slots(
                list(_slots),
                model,
                employee_slots,
                self.employee_hours,
                self.total_hours,
                self.offset,
            )


def _distribute_slots(
    slots: Sequence[Slot],
    model,
    employee_slots,
    employee_hours,
    total_hours,
    offset,
):
    total_shifts = sum(slot.n_employees for slot in slots)

    for id, hours in employee_hours.items():
        n_shifts_employee = hours / total_hours * total_shifts
        min_shifts_employee, max_shifts_employee = _get_bounds(
            n_shifts_employee, offset
        )

        sum_employee_slots = sum(
            employee_slots[get_key(id, slot.shift)] for slot in slots
        )
        model.Add(min_shifts_employee <= sum_employee_slots)
        model.Add(sum_employee_slots <= max_shifts_employee)


def _get_bounds(value: float, offset: int = 0) -> tuple[int, int]:
    if value.is_integer():
        return int(value) - offset, int(value) + offset
    else:
        return floor(value) - offset, ceil(value) + offset
