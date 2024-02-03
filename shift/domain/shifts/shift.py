from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from datetime import timedelta
from itertools import product
from typing import Iterable, Iterator, Sequence, Set, TypeVar, Union

from shift.domain.shifts.days import Day, WeekDay, WeekDays
from shift.domain.shifts.periods import Period
from shift.domain.utils.model import Model

RegularShiftDuration = 8


@dataclass
class Shift(Model):
    """_summary_

    Arguments:
        Model -- _description_

    Returns:
        _description_
    """

    period: Period
    day: Day
    duration: int = 8

    def __lt__(self, other: Shift) -> bool:
        if not isinstance(other, Shift):
            return NotImplemented
        if self.day < other.day:
            return True
        if self.day == other.day:
            return self.period < other.period
        return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Shift):
            return NotImplemented
        if self.day == other.day and self.period == other.period:
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.period.name} shift on {self.day}"

    def __hash__(self) -> int:
        return hash((self.period, self.day, self.duration))


S = TypeVar("S", bound=Shift)


@dataclass()
class Planned(Shift):
    employee_ids: Set[int] = field(default_factory=set)

    def is_complete(self, target: Union[int, Slot]) -> bool:
        if isinstance(target, Slot):
            _target = target.n_employees
        else:
            _target = target

        if len(self.employee_ids) >= _target:
            return True
        return False

    def __repr__(self) -> str:
        _repr = "planned " + super().__repr__()
        if self.employee_ids:
            _repr += f", for ids: {self.employee_ids}"
        return _repr


@dataclass(eq=True)
class Slot(Shift):
    n_employees: int = 1

    @property
    def shift(self) -> Shift:
        return Shift(self.period, self.day, self.duration)

    def __repr__(self) -> str:
        return f"slot {super().__repr__()}, for {self.n_employees} employee(s)"


def shift_range(
    *_args: Shift, periods: Iterable[Period], inclusive: bool = True
) -> Iterator[Shift]:
    if _args[1] < _args[0]:
        raise ValueError

    # get range of days between start and end
    day_range = range(
        (_args[1].day.date - _args[0].day.date + timedelta(days=1)).days
    )

    for _day, _period in product(
        (_args[0].day.date + timedelta(delta) for delta in day_range),
        sorted(period for period in periods),
    ):
        shift = Shift(_period, Day(_day))
        # Prevent shift on same day but earlier period
        if shift < _args[0]:
            continue
        # Prevent shift on same day but later period
        elif inclusive and shift > _args[1]:
            continue
        elif not inclusive and not shift < _args[1]:
            continue
        yield shift


def get_consecutive_shifts(
    shifts: Iterable[S],
    week_days: Sequence[WeekDay] = WeekDays,
    n: int = 2,
) -> Iterable[tuple[S, ...]]:
    for _shifts in _tee(shifts, n):
        if all(shift.day.week_day in week_days for shift in _shifts):
            yield _shifts


def _tee(shifts: Iterable[S], n: int = 2) -> Iterable[tuple[S, ...]]:
    shifts_tee = itertools.tee(shifts, n)
    for i in range(1, n):
        for _ in range(i):
            next(shifts_tee[i], None)
    return zip(*shifts_tee)
