from datetime import date

from ortools.sat.python import cp_model  # type: ignore
from pytest import fixture

from shift.domain.shifts.periods import DayAndEvening
from shift.domain.shifts.shift import Day, Slot, shift_range


@fixture
def slot_t0() -> Slot:
    return Slot(period=DayAndEvening.day, day=Day(date=date(2002, 2, 4)))


@fixture
def slot_t1_delta_4months() -> Slot:
    return Slot(period=DayAndEvening.evening, day=Day(date=date(2002, 6, 3)))


@fixture
def slot_t1_delta_1week() -> Slot:
    return Slot(period=DayAndEvening.evening, day=Day(date=date(2002, 2, 11)))


@fixture
def slots_4months(slot_t0: Slot, slot_t1_delta_4months: Slot) -> list[Slot]:
    _slots = []
    for shift in shift_range(
        slot_t0, slot_t1_delta_4months, periods=DayAndEvening
    ):
        _slots.append(
            Slot(shift.period, shift.day, shift.duration, n_employees=1)
        )
    return _slots


@fixture
def slots_1week(slot_t0: Slot, slot_t1_delta_1week: Slot) -> list[Slot]:
    _slots = []
    for shift in shift_range(
        slot_t0, slot_t1_delta_1week, periods=DayAndEvening
    ):
        _slots.append(
            Slot(shift.period, shift.day, shift.duration, n_employees=1)
        )
    return _slots


@fixture
def employee_ids() -> list[int]:
    return list(range(10))


@fixture
def model() -> cp_model.CpModel:
    return cp_model.CpModel()
