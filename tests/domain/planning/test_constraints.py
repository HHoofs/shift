from ortools.sat.python import cp_model
from pytest import fixture  # type: ignore

from shift.domain.model import EmployeeSlot
from shift.domain.planning.constraints import MaxRecurrentShifts
from shift.domain.shifts import Slot
from shift.domain.solver import Solver


@fixture
def employee_slots(
    slots: list[Slot], employee_ids: list[int], model: cp_model.CpModel
) -> dict[EmployeeSlot, cp_model.IntVar]:
    _employee_slots = {}
    for id in employee_ids:
        for slot in slots:
            _employee_slots[(id, slot.shift)] = Solver._get_employee_slot(
                model, id, slot.shift
            )
    return _employee_slots


def test_max_recurrent_shifts(
    slots: list[Slot],
    employee_ids: list[int],
    model: cp_model.CpModel,
    employee_slots: dict[EmployeeSlot, cp_model.IntVar],
):
    max_recurrent_shifts = MaxRecurrentShifts()
    max_recurrent_shifts.employee_ids = employee_ids
    max_recurrent_shifts.add_constraint(slots, model, employee_slots)
