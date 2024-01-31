from datetime import date

import pytest

from shift.domain.shifts.days import Day
from shift.domain.shifts.periods import DayAndEvening
from shift.domain.shifts.shift import Planned, Shift, Slot, shift_range


@pytest.mark.parametrize(
    "start,end,length",
    [
        (
            Shift(DayAndEvening.day, Day(date(2002, 2, 2))),
            Shift(DayAndEvening.day, Day(date(2002, 3, 3))),
            59,
        ),
        (
            Shift(DayAndEvening.evening, Day(date(2002, 2, 2))),
            Shift(DayAndEvening.day, Day(date(2002, 3, 3))),
            58,
        ),
        (
            Shift(DayAndEvening.day, Day(date(2002, 2, 2))),
            Shift(DayAndEvening.evening, Day(date(2002, 2, 2))),
            2,
        ),
        (
            Shift(DayAndEvening.day, Day(date(2002, 2, 2))),
            Shift(DayAndEvening.evening, Day(date(2003, 1, 1))),
            668,
        ),
    ],
)
@pytest.mark.parametrize("inclusive", [True, False])
def test_shift_range_length(start, end, length, inclusive):
    length = length if inclusive else length - 1
    assert (
        len(
            list(
                shift_range(
                    start, end, periods=DayAndEvening, inclusive=inclusive
                )
            )
        )
        == length
    )


def test_shift_range_start_before_end():
    start = Shift(DayAndEvening.day, Day(date(2002, 2, 2)))
    end_before_start = Shift(DayAndEvening.day, Day(date(2002, 1, 1)))
    with pytest.raises(ValueError):
        next(shift_range(start, end_before_start, periods=DayAndEvening))


@pytest.mark.parametrize(
    "start,end,length",
    [
        (
            Slot(DayAndEvening.day, Day(date(2002, 2, 2))),
            Slot(DayAndEvening.day, Day(date(2002, 3, 3))),
            59,
        ),
        (
            Planned(DayAndEvening.day, Day(date(2002, 2, 2))),
            Planned(DayAndEvening.day, Day(date(2002, 3, 3))),
            59,
        ),
        (
            Slot(DayAndEvening.day, Day(date(2002, 2, 2))),
            Planned(DayAndEvening.day, Day(date(2002, 3, 3))),
            59,
        ),
    ],
)
def test_shift_range_with_variants(start, end, length):
    _shift_range = list(shift_range(start, end, periods=DayAndEvening))
    assert len(_shift_range) == length
    assert all(isinstance(_shift, Slot) for _shift in _shift_range)
