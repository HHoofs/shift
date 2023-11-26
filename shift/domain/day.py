from dataclasses import dataclass
import datetime

import holidays

from shift.domain.model import DomainModel

holidays.list_supported_countries


WeekDay = int


@dataclass(frozen=True, eq=True)
class Day(DomainModel):
    date: datetime.date

    @property
    def weekday(self) -> WeekDay:
        return self.date.isoweekday()

    @property
    def is_weekend(self) -> bool:
        return self.weekday > 5

    @property
    def is_holiday(self) -> bool:
        return self.date in holidays.NL()

    @property
    def weeknumber(self) -> int:
        return self.date.isocalendar()[1]

    def __repr__(self) -> str:
        _day = self.date.strftime("%A %-d %B")
        _week = self.date.isocalendar()[1]
        return f"{_day} (week: {_week})"

    def __lt__(self, other):
        return self.date < other.date
