from datetime import date

from ortools.sat.python import cp_model  # type: ignore
from pytest import fixture

from shift.domain.shifts.periods import DayAndEvening
from shift.domain.shifts.shift import Day, Slot, shift_range
from shift.domain.solver.solver import Solver
from shift.domain.utils.utils import EmployeeSlot


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
def employee_slots_1week(
    slots_1week: list[Slot], employee_ids: list[int], model: cp_model.CpModel
) -> dict[EmployeeSlot, cp_model.IntVar]:
    employee_slots = {}
    for id in employee_ids:
        for slot in slots_1week:
            employee_slots[(id, slot.shift)] = Solver._get_employee_slot(
                model, id, slot.shift
            )
    return employee_slots


@fixture
def model() -> cp_model.CpModel:
    return cp_model.CpModel()
