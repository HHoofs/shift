from dataclasses import dataclass, field
from datetime import date
from typing import Iterable

from shift.domain.planning.constraints import Constraints, PlanningConstraint
from shift.domain.planning.distributions import (
    Distributions,
    PlanningDistribution,
)
from shift.domain.shifts.shift import Day, Period, Shift, Slot, shift_range
from shift.domain.utils.model import Model


@dataclass
class Planning(Model):
    first_day: date
    last_day: date
    periods: Iterable[Period]
    shift_duration: int
    employees_per_shift: int
    employee_hours: dict[int, int] = field(default_factory=dict)
    constraints: Constraints = field(default_factory=Constraints)
    distributions: Distributions = field(default_factory=Distributions)

    @property
    def shifts(self) -> Iterable[Shift]:
        first_shift = Shift(min(self.periods), Day(self.first_day))
        last_shift = Shift(max(self.periods), Day(self.last_day))

        for shift in shift_range(
            first_shift, last_shift, periods=self.periods, inclusive=True
        ):
            yield shift

    @property
    def employee_ids(self) -> list[int]:
        return [employee_id for employee_id in self.employee_hours.keys()]

    @property
    def slots(self) -> Iterable[Slot]:
        for shift in self.shifts:
            yield Slot(
                period=shift.period,
                day=shift.day,
                duration=self.shift_duration,
                n_employees=self.employees_per_shift,
            )

    def retrieve_constraints(self) -> Iterable[PlanningConstraint]:
        for constraint in self.constraints:
            constraint.employee_ids = list(
                set(constraint.employee_ids).intersection(
                    self.employee_hours.keys()
                )
            )
            yield constraint

    def retrieve_distributions(self) -> Iterable[PlanningDistribution]:
        for distribution in self.distributions:
            distribution.employee_hours = self.employee_hours
            yield distribution
