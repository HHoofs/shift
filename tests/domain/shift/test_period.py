from datetime import date

import pytest

from shift.domain.shifts.days import Day
from shift.domain.shifts.periods import DayAndEvening
from shift.domain.shifts.shift import Shift


def test_operators():
    day_period = DayAndEvening.day
    evening_period = DayAndEvening.evening

    assert day_period == day_period
    assert day_period < evening_period


def test_invalid_operators():
    day_period = DayAndEvening.day
    shift_2013 = Shift(DayAndEvening.day, Day(date(2013, 4, 30)))

    with pytest.raises(TypeError):
        day_period < shift_2013  # type: ignore

    with pytest.raises(TypeError):
        day_period <= shift_2013  # type: ignore

    assert not shift_2013 == day_period
