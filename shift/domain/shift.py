from __future__ import annotations

from datetime import timedelta
from dataclasses import dataclass, field
from enum import Flag
from itertools import product
from typing import Iterable, Set, Union

import holidays

from shift.domain.base import Model


WeekDay = int


class Period(Flag):
    morning = 1
    evening = 2

    def __lt__(self, other: Period) -> bool:
        if not isinstance(other, Period):
            return NotImplemented
        return self.value < other.value

    def __eq__(self, other: Period) -> bool:
        if not isinstance(other, Period):
            return NotImplemented
        return self.value == other.value


@dataclass(frozen=True, eq=True)
class Day:
    date: datetime.date

    @property
    def week_day(self) -> WeekDay:
        return self.date.isoweekday()

    @property
    def is_weekend(self) -> bool:
        return self.week_day > 5

    @property
    def is_holiday(self) -> bool:
        return self.date in holidays.NL()

    @property
    def week_number(self) -> int:
        return self.date.isocalendar()[1]

    def __repr__(self) -> str:
        _day = self.date.strftime("%A %-d %B")
        _week = self.date.isocalendar()[1]
        return f"{_day} (week: {_week})"

    def __lt__(self, other) -> bool:
        if not isinstance(other, Day):
            return NotImplemented
        return self.date < other.date

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Day):
            return NotImplemented
        return self.date == other.date


@dataclass
class Shift(Model):
    period: Period
    day: Day

    def __lt__(self, other: Shift) -> bool:
        if not isinstance(other, Shift):
            return NotImplemented
        if self.day < other.day:
            return True
        if self.day == other.day:
            return self.period < other.period
        return False

    def __eq__(self, other: Shift) -> bool:
        if not isinstance(other, Shift):
            return NotImplemented
        if self.day == other.day and self.period == other.period:
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.period.name} shift on {self.day}"


@dataclass(repr=True)
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


@dataclass(eq=True)
class Slot(Shift):
    n_employees: int = 1


def shift_range(*_args: Shift, inclusive: bool = True) -> Iterable[Shift]:
    start = _args[0]
    end = _args[1]
    if end < start:
        raise ValueError

    day_range = range((end.day.date - start.day.date + timedelta(days=1)).days)

    for _day, _period in product(
        (start.day.date + timedelta(delta) for delta in day_range),
        sorted(period for period in Period),
    ):
        shift = Shift(_period, Day(_day))
        if shift < start:
            continue
        elif inclusive and shift > end:
            continue
        elif not inclusive and not shift < end:
            continue
        yield shift
