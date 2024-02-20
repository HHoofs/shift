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


def test_model():
    shift = Shift(DayAndEvening.day, Day(date(2021, 1, 1)))
    assert shift.entity == "Shift"
    assert str(shift) == "day shift on Friday 1 January (week: 53)"


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


def test_consecutive_shifts(slots_4months: list[Slot]):
    consecutive_slots = list(get_consecutive_shifts(slots_4months))
    # The last slot has no consecutive shift
    assert len(consecutive_slots) == len(slots_4months) - 1

    three_consecutive_slots = list(get_consecutive_shifts(slots_4months, n=3))
    assert len(three_consecutive_slots) == len(slots_4months) - 2

    weekend_consecutive_slots = list(
        get_consecutive_shifts(slots_4months, week_days=(6, 7), n=2)
    )

    for slots in weekend_consecutive_slots:
        assert all(slot.day.week_day in (6, 7) for slot in slots)
        assert not (
            slots[0].day.week_day == 7
            and slots[0].period == DayAndEvening.evening
        )


def test_planned_is_complete(slot_t0: Slot):
    planned = Planned(slot_t0.period, slot_t0.day, slot_t0.duration)
    assert not planned.is_complete(2)
    assert planned.is_complete(0)

    planned.employee_ids = {0, 1}
    assert planned.is_complete(2)
    assert planned.is_complete(slot_t0)

    with pytest.raises(TypeError):
        planned.is_complete(None)  # type: ignore
