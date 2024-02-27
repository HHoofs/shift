import numpy as np
import pytest  # type: ignore
from google.protobuf.json_format import MessageToDict  # type: ignore
from ortools.sat.python import cp_model

from shift.domain.planning.distributions import (
    Distributions,
    NShifts,
    NShiftsMonthly,
    PlanningDistribution,
    _get_bounds,
)
from shift.domain.shifts.shift import Slot
from shift.domain.utils.utils import EmployeeSlot


def test_distributions():
    distributions = Distributions()
    distributions.add(NShifts())
    distributions.add(NShiftsMonthly())

    for distribution in distributions:
        assert isinstance(distribution, PlanningDistribution)


def test_distribution_base():
    distribution_base = PlanningDistribution()
    assert getattr(distribution_base, "add_distribution")

    with pytest.raises(NotImplementedError):
        distribution_base.add_distribution(None, None, None)  # type: ignore


@pytest.mark.parametrize(
    "distribution, expected_avg_cap_value",
    [(NShifts, 24.5), (NShiftsMonthly, 4.9)],
)
def test_add_distributions(
    employee_ids: list[int],
    slots_4months: list[Slot],
    model: cp_model,
    employee_slots_4months: dict[EmployeeSlot, cp_model.IntVar],
    distribution,
    expected_avg_cap_value,
    get_cap_value,
):
    distribute_shifts = distribution()
    distribute_shifts.employee_hours = {id: 1 for id in employee_ids}
    distribute_shifts.add_distribution(
        slots_4months, model, employee_slots_4months
    )

    initialized_model = MessageToDict(model.Proto())
    cap_values = [
        get_cap_value(constraint["linear"]["domain"])
        for constraint in initialized_model["constraints"]
    ]
    avg_cap_value = np.mean(cap_values)
    # Check that average number of shifts to be assigned matches the number
    # of shifts to be assigned
    assert avg_cap_value == expected_avg_cap_value


def test_get_bounds():
    assert _get_bounds(3, 1) == (2, 4)
