from dataclasses import dataclass, field
from datetime import date
from typing import Iterable

from shift.domain.planning.constraints import PlanningConstraint
from shift.domain.planning.distributions import Distributions
from shift.domain.shifts.shift import Day, Period, Shift, Slot, shift_range
from shift.domain.utils.model import Model


@dataclass
class Planning(Model):
    first_day: date
    last_day: date
    periods: Iterable[Period]
    shift_duration: int
    employees_per_shift: int
    employee_ids: list[int] = field(default_factory=list)
    constraints: list[PlanningConstraint] = field(default_factory=list)
    distributions: list[Distributions] = field(default_factory=list)

    @property
    def shifts(self) -> Iterable[Shift]:
        first_shift = Shift(min(self.periods), Day(self.first_day))
        last_shift = Shift(max(self.periods), Day(self.last_day))

        for shift in shift_range(
            first_shift, last_shift, periods=self.periods, inclusive=True
        ):
            yield shift

    def get_slots(self) -> Iterable[Slot]:
        for shift in self.shifts:
            yield Slot(
                period=shift.period,
                day=shift.day,
                duration=self.shift_duration,
                n_employees=self.employees_per_shift,
            )
