from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Iterable, Iterator

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpModel, LinearExprT

from shift.domain.base import Model
from shift.domain.shift import Day, Period, Shift, Slot, shift_range


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
        employee_slots: dict[str, cp_model.LinearExprT],
    ) -> None:
        raise NotImplementedError


@dataclass
class WorkersPerShift(ModelConstraint):
    def add_constraint(
        self,
        slots: Iterable[Slot],
        model: CpModel,
        employee_slots: dict[str, LinearExprT],
    ) -> None:
        for slot in slots:
            _sum = sum(
                employee_slots[...] for employee_id in self.employee_ids
            )
            model.Add(_sum == slot.n_employees)


# def workers_per_shift(
#     model: cp_model.CpModel,
#     vars: Mapping[str, cp_model.LinearExprT],
#     workers,
#     n=1,
#     *args: Iterable[DomainModels],
# ):
#     if n != 1:
#         raise ValueError(
#             f"Planning works only with 1 required worker for each shift. "
#             f"It is therefore not possible to plan with the specified "
#             f"{n} workers within each shift"
#         )

#     for key in product(*args):
#         model.AddExactlyOne(
#             vars[create_key(worker, *key)] for worker in workers
#         )
