from dataclasses import dataclass
from datetime import date
from typing import Literal, Sequence, cast

import holidays

WeekDay = Literal[1, 2, 3, 4, 5, 6, 7]
WeekDays: Sequence[WeekDay] = (1, 2, 3, 4, 5, 6, 7)
Month = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
Months: Sequence[Month] = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)


@dataclass(frozen=True, eq=True)
class Day:
    date: date

    @property
    def week_day(self) -> WeekDay:
        return cast(WeekDay, self.date.isoweekday())

    @property
    def week_number(self) -> int:
        return self.date.isocalendar()[1]

    @property
    def iso_year(self) -> int:
        return self.date.isocalendar()[0]

    @property
    def month(self) -> Month:
        return cast(Month, self.date.month)

    def is_weekend(self) -> bool:
        return self.week_day > 5

    def is_holiday(self) -> bool:
        return self.date in holidays.country_holidays("NL")

    def __repr__(self) -> str:
        _day = self.date.strftime("%A %-d %B")
        _week = self.date.isocalendar()[1]
        return f"{_day} (week: {_week})"

    def __lt__(self, other) -> bool:
        if not isinstance(other, Day):
            return NotImplemented
        return self.date < other.date

    def __le__(self, other) -> bool:
        if not isinstance(other, Day):
            return NotImplemented
        return self.date <= other.date

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Day):
            return NotImplemented
        return self.date == other.date

    def __hash__(self) -> int:
        return hash(self.date)
