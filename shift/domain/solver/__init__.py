from dataclasses import dataclass, field
from itertools import product
from typing import Iterable, Optional, Sequence

from ortools.sat.python import cp_model  # type: ignore

from shift.domain.base import Model
from shift.domain.model import EmployeeSlot, get_key
from shift.domain.planning.constraints import PlanningConstraint
from shift.domain.planning.distributions import PlanningDistribution
from shift.domain.shift import Shift, Slot
from shift.domain.solver.optimizers import PlanningOptimization


@dataclass
class Solver(Model):
    planning_id: int
    optimization: Optional[PlanningOptimization] = None
    model: cp_model.CpModel = field(default_factory=cp_model.CpModel())
    employee_slots: dict[EmployeeSlot, cp_model.IntVar] = field(
        default_factory=dict
    )
    added_constraints: list[int] = field(default_factory=list)
    added_distributions: list[int] = field(default_factory=list)

    def add_slots(
        self, employee_ids: Iterable[int], shifts: Iterable[Shift]
    ) -> None:
        for employee_id, shift in product(employee_ids, shifts):
            self.employee_slots[
                get_key(employee_id, shift)
            ] = self.model.NewBoolVar(
                f"Slot <Employee: {employee_id}; Shift: {shift}"
            )

    def add_constraints(
        self, constraints: Iterable[PlanningConstraint], slots: Sequence[Slot]
    ) -> None:
        for constraint in constraints:
            constraint.add_constraint(
                model=self.model,
                employee_slots=self.employee_slots,
                slots=slots,
            )

    def add_distributions(
        self,
        distributions: Iterable[PlanningDistribution],
        slots: Sequence[Slot],
    ) -> None:
        for distribution in distributions:
            distribution.add_distribution(
                model=self.model,
                employee_slots=self.employee_slots,
                slots=slots,
            )
