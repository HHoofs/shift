from datetime import timedelta

import pytest
from google.protobuf.json_format import MessageToDict

from shift.domain.planning.constraints import SpecificShifts
from shift.domain.shifts.periods import DayAndEvening
from shift.domain.solver.solver import Solver


@pytest.fixture
def solver(model, employee_ids, shifts_1week) -> Solver:
    solver = Solver(0, employee_ids, shifts_1week, model=model)
    return solver


def test_add_slots(
    solver: Solver,
    employee_ids: list[int],
    delta_1week: timedelta,
):
    initialized_model = MessageToDict(solver.model.Proto())

    variables = initialized_model["variables"]

    assert len(variables) == len(employee_ids) * (delta_1week.days + 1) * len(
        DayAndEvening
    )

    n_wednesday, n_employee_0, n_day_shift = 0, 0, 0

    for variable in variables:
        var_name, domain = variable["name"], variable["domain"]

        assert domain == ["0", "1"]
        if "Wednesday" in var_name:
            n_wednesday += 1
        if "Employee: 0" in var_name:
            n_employee_0 += 1
        if "day shift" in var_name:
            n_day_shift += 1

    assert n_wednesday == len(employee_ids) * len(DayAndEvening)
    assert n_employee_0 == (delta_1week.days + 1) * len(DayAndEvening)
    assert n_day_shift == len(employee_ids) * (delta_1week.days + 1)


def test_add_constraints(
    solver: Solver, slot_t0, slot_t1_delta_1week, slots_1week, employee_ids
):
    block_first_shift = SpecificShifts(shifts=[slot_t0.shift])
    block_first_shift.employee_ids = [employee_ids[0]]

    block_last_shift = SpecificShifts(shifts=[slot_t1_delta_1week.shift])
    block_last_shift.employee_ids = [employee_ids[-1]]

    solver.add_constraints([block_first_shift, block_last_shift], slots_1week)
    initialized_model = MessageToDict(solver.model.Proto())
    constraints = initialized_model["constraints"]

    assert len(constraints) == 2

    first_constraint = constraints[0]["linear"]
    assert first_constraint["vars"] == [0]
    assert max(map(int, first_constraint["domain"][1])) == 0

    last_constraint = constraints[0]["linear"]
    assert max(map(int, last_constraint["domain"][1])) == 0
