from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from shift.domain.model import DomainModel
from shift.domain.typing import DayBlock


class PreferenceMode(Enum):
    BALANCED = 1
    UNAVAILABLE = 2
    PREFERRED = 3


@dataclass(frozen=True, eq=True)
class Preference(DomainModel):
    Category: PreferenceMode


@dataclass(frozen=True, eq=True)
class DayPreference(Preference):
    day: DayBlock


class DaysBalance(Preference):
    days: Sequence[DayBlock]
