from __future__ import annotations

from enum import Flag


class Period(Flag):
    ...

    def __lt__(self, other: Period) -> bool:
        if not isinstance(other, Period):
            return NotImplemented
        return self.value < other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Period):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return super().__hash__()


class DayAndEvening(Period):
    day = 1
    evening = 2
