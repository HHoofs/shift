from datetime import date

import pytest

from shift.domain.shifts.days import Day
from shift.domain.shifts.periods import DayAndEvening
from shift.domain.shifts.shift import (
    Planned,
    Shift,
    Slot,
    get_consecutive_shifts,
    shift_range,
)


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
def test_shift_range_length(
    start: Shift, end: Shift, length: int, inclusive: bool
):
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


def test_shift_range_start_before_end(
    slot_t0: Slot, slot_t1_delta_4months: Slot
):
    with pytest.raises(ValueError):
        next(
            shift_range(slot_t1_delta_4months, slot_t0, periods=DayAndEvening)
        )


@pytest.mark.parametrize(
    "start,end",
    [
        (
            Slot(DayAndEvening.day, Day(date(2002, 2, 2))),
            Slot(DayAndEvening.day, Day(date(2002, 3, 3))),
        ),
        (
            Planned(DayAndEvening.day, Day(date(2002, 2, 2))),
            Planned(DayAndEvening.day, Day(date(2002, 3, 3))),
        ),
        (
            Slot(DayAndEvening.day, Day(date(2002, 2, 2))),
            Planned(DayAndEvening.day, Day(date(2002, 3, 3))),
        ),
    ],
)
def test_shift_range_with_variants(start: Shift, end: Shift):
    _shift_range = list(shift_range(start, end, periods=DayAndEvening))

    assert len(_shift_range) == 59
    assert all(isinstance(_shift, Shift) for _shift in _shift_range)


def test_consecutive_shifts(slots: list[Slot]):
    consecutive_slots = list(get_consecutive_shifts(slots))
    # The last slot has no consecutive shift
    assert len(consecutive_slots) == len(slots) - 1

    three_consecutive_slots = list(get_consecutive_shifts(slots, n=3))
    assert len(three_consecutive_slots) == len(slots) - 2

    weekend_consecutive_slots = list(
        get_consecutive_shifts(slots, week_days=(6, 7), n=2)
    )

    for consecutive_slots in weekend_consecutive_slots:
        assert all(slot.day.week_day in (6, 7) for slot in consecutive_slots)
        assert not (
            consecutive_slots[0].day.week_day == 7
            and consecutive_slots[0].period == DayAndEvening.evening
        )
