from shift.domain.employee.specifications import (
    Holiday,
    Specification,
    Specifications,
    SpecificDay,
    SpecificPeriod,
    SpecificShift,
    SpecificWeekDay,
    SpecType,
)
from shift.domain.shifts.periods import DayAndEvening
from shift.domain.shifts.shift import Slot


def test_spec_type():
    assert SpecType.UNAVAILABLE < SpecType.MANDATORY


def test_specific_shift(slot_t0: Slot, slot_t1_delta_1week: Slot):
    specific_shift = SpecificShift(SpecType.UNAVAILABLE, slot_t0.shift)
    assert specific_shift.spec_for_shift(slot_t0.shift) == SpecType.UNAVAILABLE
    assert specific_shift.spec_for_shift(slot_t1_delta_1week.shift) is None


def test_specific_day(slot_t0: Slot, slot_t1_delta_1week: Slot):
    specific_day = SpecificDay(SpecType.UNAVAILABLE, slot_t0.day)
    assert specific_day.spec_for_shift(slot_t0.shift) == SpecType.UNAVAILABLE
    assert specific_day.spec_for_shift(slot_t1_delta_1week.shift) is None


def test_specific_period(slot_t0: Slot, slot_t1_delta_1week: Slot):
    specific_period = SpecificPeriod(
        SpecType.UNAVAILABLE, DayAndEvening.evening
    )
    assert specific_period.spec_for_shift(slot_t0.shift) is None
    assert (
        specific_period.spec_for_shift(slot_t1_delta_1week.shift)
        == SpecType.UNAVAILABLE
    )


def test_holiday(
    slot_t0: Slot, slot_t1_delta_1week: Slot, slot_t1_delta_4months: Slot
):
    holiday = Holiday(slot_t0.shift, slot_t1_delta_1week.shift)
    assert holiday.spec_for_shift(slot_t0) == SpecType.UNAVAILABLE_COR
    assert holiday.spec_for_shift(slot_t1_delta_4months) is None

    assert slot_t1_delta_1week in holiday.shifts
    assert len(list(holiday.days)) == 8
    assert holiday.n_shifts == 16
    assert holiday.n_days == 8


def test_specific_week_day(slot_t0: Slot, slot_t1_delta_4months: Slot):
    specific_week_day = SpecificWeekDay(
        SpecType.UNAVAILABLE, slot_t0.day.week_day
    )
    assert (
        specific_week_day.spec_for_shift(slot_t0.shift) == SpecType.UNAVAILABLE
    )
    assert (
        specific_week_day.spec_for_shift(slot_t1_delta_4months.shift) is None
    )


def test_specifications(slot_t0: Slot, slot_t1_delta_1week: Slot):
    specifications = Specifications(1)
    specifications.add(SpecificShift(SpecType.UNAVAILABLE_COR, slot_t0.shift))
    specifications.add(SpecificDay(SpecType.UNAVAILABLE, slot_t0.day))
    specifications.add(SpecificPeriod(SpecType.UNAVAILABLE, DayAndEvening.day))
    specifications.add(
        SpecificWeekDay(SpecType.UNAVAILABLE, slot_t0.day.week_day)
    )

    for specification in specifications:
        assert isinstance(specification, Specification)

    assert (
        len(specifications.blocked_days(slot_t0.day, slot_t1_delta_1week.day))
        == 1
    )
