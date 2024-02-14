import pytest
from google.protobuf.json_format import MessageToDict

from shift.domain.shifts.shift import Slot
from shift.domain.solver.optimizers import PlanningOptimization


def test_entity():
    optimizer = PlanningOptimization([1])
    assert optimizer.entity == "PlanningOptimization"


@pytest.mark.parametrize("week_days", [(1,), (7, 3, 5), (1, 2, 3, 4, 5, 6, 7)])
def test_add_optimization(
    slots_1week: list[Slot],
    employee_ids,
    employee_slots_1week,
    model,
    week_days,
):
    optimizer = PlanningOptimization(employee_ids, week_days=week_days)

    optimizer.add_optimization(
        slots_1week,
        model,
        employee_slots_1week,
    )

    constrained_model = MessageToDict(model.Proto())
    constraints = constrained_model["constraints"]

    n_expected_constraints = (len(week_days) + 1) * len(employee_ids)

    assert len(constraints) == n_expected_constraints
