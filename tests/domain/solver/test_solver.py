from datetime import timedelta
from statistics import mean

import numpy as np
import pytest
from google.protobuf.json_format import MessageToDict

from shift.domain.planning.constraints import SpecificShifts
from shift.domain.planning.distributions import NShifts
from shift.domain.shifts.periods import DayAndEvening
from shift.domain.solver.solver import Solver


@pytest.fixture
def solver_1week(model, employee_ids, slots_1week) -> Solver:
    solver = Solver(0, employee_ids, slots_1week, model=model)
    return solver


@pytest.fixture
def solver_4months(model, employee_ids, slots_4months) -> Solver:
    solver = Solver(0, employee_ids, slots_4months, model=model)
    return solver


def test_add_slots(
    solver_1week: Solver,
    employee_ids: list[int],
    delta_1week: timedelta,
):
    initialized_model = MessageToDict(solver_1week.model.Proto())

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
    solver_1week: Solver, slot_t0, slot_t1_delta_1week, employee_ids
):
    block_first_shift = SpecificShifts(shifts=[slot_t0.shift])
    block_first_shift.employee_ids = [employee_ids[0]]

    block_last_shift = SpecificShifts(shifts=[slot_t1_delta_1week.shift])
    block_last_shift.employee_ids = [employee_ids[-1]]

    solver_1week.add_constraints([block_first_shift, block_last_shift])
    initialized_model = MessageToDict(solver_1week.model.Proto())
    constraints = initialized_model["constraints"]

    assert len(constraints) == 2

    first_shift_constraint = constraints[0]["linear"]
    assert first_shift_constraint["vars"] == [0]
    assert max(map(int, first_shift_constraint["domain"][1])) == 0

    last_shift_constraint = constraints[1]["linear"]
    # Find max potential index
    assert last_shift_constraint["vars"] == [
        len(initialized_model["variables"]) - 1
    ]
    assert max(map(int, last_shift_constraint["domain"][1])) == 0


def test_add_distributions(solver_4months: Solver, employee_ids: list[int]):
    distribute_shifts = NShifts()
    distribute_shifts.employee_hours = {id: 1 for id in employee_ids}

    solver_4months.add_distributions([distribute_shifts])
    initialized_model = MessageToDict(solver_4months.model.Proto())
    cap_values = [
        get_cap_value(constraint["linear"]["domain"])
        for constraint in initialized_model["constraints"]
    ]
    avg_cap_value = mean(cap_values)
    assert np.isclose(
        avg_cap_value * len(employee_ids),
        len(list(solver_4months._slots)),
        atol=len(employee_ids),
    )


def get_cap_value(domain: list[str]) -> int:
    return min(list(map(int, domain)), key=abs)
