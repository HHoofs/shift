from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import IntEnum
from functools import cached_property
from typing import Iterable, Iterator, Optional, Union

from shift.domain.base import Model
from shift.domain.shift import Day, Period, Shift, WeekDay, shift_range


class SpecType(IntEnum):
    UNAVAILABLE_COR = -9
    UNAVAILABLE = -2
    NOT_PREFERRED = -1
    PREFERRED = 1
    MANDATORY = 2


@dataclass
class Specifications(Model):
    employee_id: int
    shifts: list[SpecificShift] = field(default_factory=list)
    days: list[SpecificDay] = field(default_factory=list)
    periods: list[SpecificPeriod] = field(default_factory=list)
    week_day: list[SpecificWeekDay] = field(default_factory=list)
    holidays: list[Holiday] = field(default_factory=list)

    def add(self, specification) -> None:
        if isinstance(specification, SpecificShift):
            self.shifts.append(specification)
        elif isinstance(specification, SpecificDay):
            self.days.append(specification)
        elif isinstance(specification, SpecificPeriod):
            self.periods.append(specification)
        elif isinstance(specification, SpecificWeekDay):
            self.week_day.append(specification)
        elif isinstance(specification, Holiday):
            self.holidays.append(specification)
        else:
            raise

    def __iter__(self) -> Iterator[Union[Specification, Holiday]]:
        yield from self.shifts
        yield from self.days
        yield from self.periods
        yield from self.week_day
        yield from self.holidays

    def min_for_shift(self, shift: Shift) -> Optional[SpecType]:
        return min(
            spec_type
            for specification in self
            if (spec_type := specification.spec_for_shift(shift))
        )

    def blocked_days(
        self, start_day: Day, end_day: Day
    ) -> dict[date, list[Day]]:
        blocked_days = defaultdict(list)
        day = start_day
        while day <= end_day:
            if all(
                self.min_for_shift(Shift(period, day))
                is SpecType.UNAVAILABLE_COR
                for period in Period
            ):
                blocked_days[day.date.replace(day=1)].append(day)
            day = Day(day.date + timedelta(days=1))
        return blocked_days


@dataclass
class Specification(Model, ABC):
    spec_type: SpecType

    @abstractmethod
    def spec_for_shift(self, shift: Shift) -> Optional[SpecType]:
        raise NotImplementedError


@dataclass
class SpecificShift(Specification):
    shift: Shift

    def spec_for_shift(self, shift: Shift) -> Optional[SpecType]:
        return self.spec_type if shift == self.shift else None


@dataclass
class SpecificDay(Specification):
    day: Day

    def spec_for_shift(self, shift: Shift) -> Optional[SpecType]:
        return self.spec_type if shift.day == self.day else None


@dataclass
class SpecificPeriod(Specification):
    period: Period

    def spec_for_shift(self, shift: Shift) -> Optional[SpecType]:
        return self.spec_type if shift.period == self.period else None


@dataclass
class SpecificWeekDay(Specification):
    week_day: WeekDay

    def spec_for_shift(self, shift: Shift) -> Optional[SpecType]:
        return self.spec_type if shift.day.week_day == self.week_day else None


@dataclass
class Holiday(Model):
    first_shift: Shift
    last_shift: Shift
    spec_type = SpecType.UNAVAILABLE_COR

    def spec_for_shift(self, shift: Shift) -> Optional[SpecType]:
        return self.spec_type if shift in self.shifts else None

    @cached_property
    def shifts(self) -> Iterable[Shift]:
        periods = self.first_shift.period.__class__
        if not isinstance(self.last_shift, periods):
            raise ValueError(
                "The first and last shift should be specified using the same periods"
            )

        return shift_range(
            self.first_shift, self.last_shift, periods=periods, inclusive=True
        )

    @property
    def days(self) -> Iterable[Day]:
        return set(shift.day for shift in self.shifts)

    @property
    def n_shifts(self) -> int:
        return len(list(self.shifts))

    @property
    def n_days(self) -> int:
        return len(list(self.days))
