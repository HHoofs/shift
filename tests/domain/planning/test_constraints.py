import re

import pytest  # type: ignore
from google.protobuf.json_format import MessageToDict  # type: ignore
from ortools.sat.python import cp_model  # type: ignore

from shift.domain.planning.constraints import (
    Constraints,
    MaxConsecutiveShifts,
    MaxRecurrentShifts,
    PlanningConstraint,
    ShiftsPerDay,
    SpecificShifts,
    WorkersPerShift,
)
from shift.domain.shifts.shift import Slot
from shift.domain.utils.utils import EmployeeSlot


def test_constraint_model():
    constraints = Constraints()
    assert constraints.entity == "Constraints"
    with pytest.raises(AttributeError):
        assert str(constraints)


@pytest.fixture
def workers_per_shift():
    return WorkersPerShift()


@pytest.fixture
def shifts_per_day():
    return ShiftsPerDay()


@pytest.fixture
def specific_shifts():
    return SpecificShifts()


@pytest.fixture
def max_consecutive_shifts():
    return MaxConsecutiveShifts()


@pytest.fixture
def max_recurrent_shifts():
    return MaxRecurrentShifts()


def test_constraint_add(
    workers_per_shift: PlanningConstraint,
    shifts_per_day: PlanningConstraint,
    specific_shifts: PlanningConstraint,
    max_consecutive_shifts: PlanningConstraint,
    max_recurrent_shifts: PlanningConstraint,
):
    constraints = Constraints()

    constraints.add(workers_per_shift)
    constraints.add(shifts_per_day)
    constraints.add(specific_shifts, [1])
    constraints.add(max_consecutive_shifts)
    constraints.add(max_recurrent_shifts)

    assert len(list(constraints)) == 5


@pytest.mark.parametrize("max", [1, 2, 3])
@pytest.mark.parametrize("n_employees", [1, 2, 3])
def test_max_recurrent_shifts(
    slots_1week: list[Slot],
    model: cp_model.CpModel,
    employee_slots_1week: dict[EmployeeSlot, cp_model.IntVar],
    max: int,
    n_employees: int,
):
    max_recurrent_shifts = MaxRecurrentShifts(max=max)

    # check fixed window
    assert max_recurrent_shifts.window == 2

    # add employees and add constraint
    max_recurrent_shifts.employee_ids = list(range(n_employees))
    max_recurrent_shifts.add_constraint(
        slots_1week, model, employee_slots_1week
    )

    constrained_model = MessageToDict(model.Proto())
    constraints = constrained_model["constraints"]
    variables = constrained_model["variables"]

    assert len(constraints) == n_employees
    for constraint in constraints:
        assert all(
            any(
                day in variables[var_idx]["name"]
                for day in ("Saturday", "Sunday")
            )
            for var_idx in constraint["linear"]["vars"]
        )
        assert int(constraint["linear"]["domain"][1]) == max


@pytest.mark.parametrize("max", [1, 2, 10])
@pytest.mark.parametrize("window", [1, 2, 10])
def test_max_consecutive_shifts(
    slots_1week: list[Slot],
    model: cp_model.CpModel,
    employee_slots_1week: dict[EmployeeSlot, cp_model.IntVar],
    max: int,
    window: int,
    get_cap_value,
):
    max_recurrent_shifts = MaxConsecutiveShifts(max=max, window=window)
    max_recurrent_shifts.employee_ids = [0]
    max_recurrent_shifts.add_constraint(
        slots_1week, model, employee_slots_1week
    )

    constrained_model = MessageToDict(model.Proto())
    constraints = constrained_model["constraints"]

    for constraint in constraints:
        assert len(constraint["linear"]["vars"]) == window
        assert get_cap_value(constraint["linear"]["domain"]) == max


def test_specific_shifts(
    employee_ids: list[int],
    slots_1week: list[Slot],
    model: cp_model,
    employee_slots_1week: dict[EmployeeSlot, cp_model.IntVar],
    slot_t0: Slot,
    slot_t1_delta_1week: Slot,
    get_cap_value,
):
    block_first_shift = SpecificShifts(specific_shifts=[(slot_t0.shift, True)])
    block_first_shift.employee_ids = [employee_ids[0]]

    block_last_shift = SpecificShifts(
        specific_shifts=[(slot_t1_delta_1week.shift, False)]
    )
    block_last_shift.employee_ids = [employee_ids[-1]]

    block_first_shift.add_constraint(slots_1week, model, employee_slots_1week)
    block_last_shift.add_constraint(slots_1week, model, employee_slots_1week)

    initialized_model = MessageToDict(model.Proto())
    constraints = initialized_model["constraints"]

    assert len(constraints) == 2

    first_shift_constraint = constraints[0]["linear"]
    assert first_shift_constraint["vars"] == [0]
    assert get_cap_value(first_shift_constraint["domain"]) == 0

    last_shift_constraint = constraints[1]["exactlyOne"]
    # Find max potential index
    assert last_shift_constraint["literals"] == [
        len(initialized_model["variables"]) - 1
    ]


def test_specific_shifts_multiple_employees(
    employee_ids: list[int],
    slots_1week: list[Slot],
    model: cp_model,
    employee_slots_1week: dict[EmployeeSlot, cp_model.IntVar],
    slot_t0: Slot,
):
    block_first_shift = SpecificShifts(specific_shifts=[(slot_t0.shift, True)])
    block_first_shift.employee_ids = employee_ids[0:3]

    with pytest.raises(ValueError):
        block_first_shift.add_constraint(
            slots_1week, model, employee_slots_1week
        )


@pytest.mark.parametrize("n_employees", [1, 2, 20])
def test_workers_per_shift(
    slots_1week: list[Slot],
    model: cp_model,
    employee_slots_1week: dict[EmployeeSlot, cp_model.IntVar],
    employee_ids: list[int],
    n_employees: int,
):
    # set number of employees required
    for slot in slots_1week:
        slot.n_employees = n_employees

    workers_per_shift = WorkersPerShift()
    workers_per_shift.employee_ids = employee_ids
    workers_per_shift.add_constraint(slots_1week, model, employee_slots_1week)

    initialized_model = MessageToDict(model.Proto())
    constraints = initialized_model["constraints"]
    variables = initialized_model["variables"]

    constraint = constraints[0]["linear"]

    assert (
        len(
            {
                variables[var]["name"].split("; ")[1]
                for var in constraint["vars"]
            }
        )
        == 1
    )

    assert all(int(limit) == n_employees for limit in constraint["domain"])


def test_shifts_per_day(
    slots_1week: list[Slot],
    model: cp_model,
    employee_slots_1week: dict[EmployeeSlot, cp_model.IntVar],
    employee_ids: list[int],
):
    shifts_per_day = ShiftsPerDay()
    shifts_per_day.employee_ids = employee_ids
    shifts_per_day.add_constraint(slots_1week, model, employee_slots_1week)

    initialized_model = MessageToDict(model.Proto())
    constraints = initialized_model["constraints"]
    variables = initialized_model["variables"]

    assert all(
        key == "atMostOne" and len(value["literals"]) == 2
        for constraint in constraints
        for key, value in constraint.items()
    )

    constraint = constraints[0]["atMostOne"]
    vars_without_period = set()

    for index in constraint["literals"]:
        var = variables[index]["name"]
        var_without_period = re.sub(r" (day|evening) shift on", "", var)
        vars_without_period.add(var_without_period)
    assert len(vars_without_period) == 1

    # check fixed property (only work one time a day)
    assert shifts_per_day.n == 1
