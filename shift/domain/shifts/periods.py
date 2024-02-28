from __future__ import annotations

from enum import IntEnum


class Period(IntEnum):
    ...

    def __hash__(self) -> int:
        return super().__hash__()


class DayAndEvening(Period):
    day = 1
    evening = 2
