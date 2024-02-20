from datetime import date

import pytest

from shift.domain.shifts.days import Day
from shift.domain.shifts.periods import DayAndEvening
from shift.domain.shifts.shift import Shift


def test_day():
    day = Day(date(2002, 5, 5))
    assert day.month == 5
    assert day.is_weekend()


def test_holiday():
    day = Day(date(2020, 1, 1))
    assert day.is_holiday()


def test_operators():
    day_2013 = Day(date(2013, 4, 30))
    day_2002 = Day(date(2002, 2, 2))

    assert day_2002 < day_2013
    assert day_2002 <= day_2013
    assert not day_2002 == day_2013


def test_invalid_operators():
    day_2013 = Day(date(2013, 4, 30))
    shift_2013 = Shift(DayAndEvening.day, day_2013)

    with pytest.raises(TypeError):
        day_2013 < shift_2013  # type: ignore

    with pytest.raises(TypeError):
        day_2013 <= shift_2013  # type: ignore

    assert not shift_2013 == day_2013
