import pytest  # type: ignore
from google.protobuf.json_format import MessageToDict
from ortools.sat.python import cp_model

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


def test_constraint_model(employee_ids: list[int]):
    constraints = Constraints(employee_ids)
    assert constraints.employee_ids == employee_ids
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
    employee_ids: list[int],
    workers_per_shift: PlanningConstraint,
    shifts_per_day: PlanningConstraint,
    specific_shifts: PlanningConstraint,
    max_consecutive_shifts: PlanningConstraint,
    max_recurrent_shifts: PlanningConstraint,
):
    constraints = Constraints(employee_ids)

    constraints.add(workers_per_shift)
    constraints.add(shifts_per_day)
    constraints.add(specific_shifts)
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
