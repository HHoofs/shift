import datetime
from datetime import date, timedelta

from ortools.sat.python import cp_model  # type: ignore
from pytest import fixture

from shift.domain.shifts.periods import DayAndEvening
from shift.domain.shifts.shift import Day, Slot, shift_range
from shift.domain.solver.solver import Solver
from shift.domain.utils.utils import EmployeeSlot


@fixture
def t0() -> datetime.date:
    return date(2002, 2, 4)


@fixture
def delta_1week() -> timedelta:
    return timedelta(days=7)


@fixture
def delta_4months() -> timedelta:
    return timedelta(days=30 * 4)


@fixture
def slot_t0(t0) -> Slot:
    return Slot(period=DayAndEvening.day, day=Day(date=t0))


@fixture
def slot_t1_delta_4months(t0, delta_4months) -> Slot:
    return Slot(period=DayAndEvening.evening, day=Day(date=t0 + delta_4months))


@fixture
def slot_t1_delta_1week(t0, delta_1week) -> Slot:
    return Slot(period=DayAndEvening.evening, day=Day(date=t0 + delta_1week))


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
def employee_slots_1week(
    slots_1week: list[Slot], employee_ids: list[int], model: cp_model.CpModel
) -> dict[EmployeeSlot, cp_model.IntVar]:
    employee_slots = {
        (employee_id, shift): model.NewBoolVar(
            f"Slot <Employee: {employee_id}; Shift: {shift}"
        )
        for employee_id, shift in Solver._get_employee_slots(
            employee_ids, slots_1week
        )
    }
    return employee_slots


@fixture
def employee_slots_4months(
    slots_4months: list[Slot], employee_ids: list[int], model: cp_model.CpModel
) -> dict[EmployeeSlot, cp_model.IntVar]:
    employee_slots = {
        (employee_id, shift): model.NewBoolVar(
            f"Slot <Employee: {employee_id}; Shift: {shift}"
        )
        for employee_id, shift in Solver._get_employee_slots(
            employee_ids, slots_4months
        )
    }
    return employee_slots


@fixture
def model() -> cp_model.CpModel:
    return cp_model.CpModel()


@fixture
def get_cap_value():
    def _get_cap_value(domain: list[str]) -> int:
        return min(list(map(int, domain)), key=abs)

    return _get_cap_value
