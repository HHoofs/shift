from __future__ import annotations

from abc import ABC
from calendar import month_name
from collections import defaultdict
from dataclasses import dataclass, field, fields
from datetime import date, timedelta
from enum import Enum, Flag, auto
from typing import Iterable, Optional, Sequence

from dateutil.relativedelta import relativedelta

from shift.domain.base import Model
from shift.domain.shift import Day, Period, Shift, WeekDay, shift_range


@dataclass(repr=True)
class Employee(Model):
    id: int
    name: str
    contract_hours: int
    specifications: Specifications
    events: list = []

    def __repr__(self) -> str:
        return self.name

    def add_specification(self, specification: Specification) -> None:
        self.specifications.add(specification)

    def __eq__(self, other: Employee) -> bool:
        if not isinstance(other, Employee):
            return NotImplemented
        return self.id == other.id


class SpecType(Enum):
    UNAVAILABLE = auto()
    NOT_PREFERRED = auto()
    PREFERRED = auto()
    MANDATORY = auto()


@dataclass
class Specifications(Model):
    shifts: list[SpecificShift] = field(default_factory=list)
    days: list[SpecificDay] = field(default_factory=list)
    period: list[SpecificPeriod] = field(default_factory=list)
    week_day: list[SpecificWeekDay] = field(default_factory=list)
    holidays: list[Holiday] = field(default_factory=list)

    def add(self, specification) -> None:
        if isinstance(specification, SpecificShift):
            self.shifts.append(specification)
        elif isinstance(specification, SpecificDay):
            self.days.append(specification)
        elif isinstance(specification, SpecificPeriod):
            self.period.append(specification)
        elif isinstance(specification, SpecificWeekDay):
            self.week_day.append(specification)
        elif isinstance(specification, Holiday):
            self.holidays.append(specification)
        else:
            raise

    def blocked_days(
        self, start_month: date, end_month: date
    ) -> dict[date, list[date]]:
        blocked_days = defaultdict(list)
        _day = start_month
        while _day <= end_month:
            if (
                any(
                    _day == spec.shift.day
                    for spec in self.shifts
                    if spec.fte_correction
                )
                or any(
                    _day == spec.day
                    for spec in self.days
                    if spec.fte_correction
                )
                or any(
                    _day.isoweekday() == spec.week_day
                    for spec in self.week_day
                    if spec.fte_correction
                )
                or any(
                    _day in [day.date for day in spec.days]
                    for spec in self.holidays
                    if spec.fte_correction
                )
            ):
                blocked_days[_day.replace(day=1)].append(_day)
            _day += timedelta(days=1)
        return blocked_days


@dataclass
class Specification(Model):
    spec_type: SpecType
    fte_correction: bool

    def __post_init__(self):
        if self.spec_type != SpecType.UNAVAILABLE and self.fte_correction:
            raise


@dataclass
class SpecificShift(Specification):
    shift: Shift


@dataclass
class SpecificDay(Specification):
    day: Day


@dataclass
class SpecificPeriod(Specification):
    period: Period


@dataclass
class SpecificWeekDay(Specification):
    week_day: WeekDay


@dataclass
class Holiday(Model):
    first_shift: Shift
    last_shift: Shift
    spec_type = SpecType.UNAVAILABLE
    fte_correction = True

    @property
    def shifts(self) -> Iterable[Shift]:
        return shift_range(self.first_shift, self.last_shift, inclusive=True)

    @property
    def days(self) -> Iterable[Day]:
        return set(shift.day for shift in self.shifts)

    @property
    def n_shifts(self) -> int:
        return len(list(self.shifts))

    @property
    def n_days(self) -> int:
        return len(list(self.days))
