from __future__ import annotations

from dataclasses import dataclass, field
from enum import Flag
from typing import Sequence

from shift.domain.base import Model
from shift.domain.shift import Shift


@dataclass(repr=True)
class Employee(Model):
    id: int
    name: str
    contract_hours: int
    events: list = []
    preferences: list[Preference] = field(default_factory=list)

    def __repr__(self) -> str:
        return self.name

    def add_preference(self, preference: Preference) -> None:
        self.preferences.append(preference)

    def __eq__(self, other: Employee) -> bool:
        if not isinstance(other, Employee):
            return NotImplemented
        return self.id == other.id


class PreferenceType(Flag):
    UNAVAILABLE = False
    PREFERRED = True


@dataclass
class Preference(Model):
    ...


@dataclass
class Slot(Preference):
    day: Shift
    preference: PreferenceType


@dataclass
class Holiday(Preference):
    first_day: Shift
    last_day: Shift

    @property
    def preference(self) -> PreferenceType:
        return PreferenceType.UNAVAILABLE

    @property
    def shifts(self) -> Sequence[Shift]:
        ...
