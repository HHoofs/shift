import pytest  # type: ignore
from google.protobuf.json_format import MessageToDict
from ortools.sat.python import cp_model

from shift.domain.planning.constraints import MaxRecurrentShifts
from shift.domain.shifts.shift import Slot
from shift.domain.utils.utils import EmployeeSlot


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
