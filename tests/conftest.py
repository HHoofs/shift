from datetime import date

from ortools.sat.python import cp_model  # type: ignore
from pytest import fixture

from shift.domain.shifts import Day, DayAndEvening, Slot, shift_range


@fixture
def slot_t0() -> Slot:
    return Slot(period=DayAndEvening.morning, day=Day(date=date(2002, 2, 4)))


@fixture
def slot_t1() -> Slot:
    return Slot(period=DayAndEvening.morning, day=Day(date=date(2002, 6, 3)))


@fixture
def slots(slot_t0: Slot, slot_t1: Slot) -> list[Slot]:
    _slots = []
    for shift in shift_range(slot_t0, slot_t1, periods=DayAndEvening):
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
