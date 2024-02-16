from dataclasses import InitVar, dataclass, field
from itertools import product
from typing import Iterable, Optional, Sequence

from ortools.sat.python import cp_model  # type: ignore

from shift.domain.planning.constraints import PlanningConstraint
from shift.domain.planning.distributions import PlanningDistribution
from shift.domain.shifts.shift import Shift, Slot
from shift.domain.solver.optimizers import PlanningOptimization
from shift.domain.utils.model import Model
from shift.domain.utils.utils import EmployeeSlot, get_key


@dataclass
class Solver(Model):
    planning_id: int
    employee_ids: InitVar[Iterable[int]]
    shifts: InitVar[Iterable[Shift]]
    optimization: Optional[PlanningOptimization] = None
    model: cp_model.CpModel = field(default_factory=cp_model.CpModel())
    employee_slots: dict[EmployeeSlot, cp_model.IntVar] = field(
        init=False, default_factory=dict
    )

    def __post_init__(
        self, employee_ids: Iterable[int], shifts: Iterable[Shift]
    ):
        for employee_id, shift in self._get_slots(employee_ids, shifts):
            self.employee_slots[
                get_key(employee_id, shift)
            ] = self.model.NewBoolVar(
                f"Slot <Employee: {employee_id}; Shift: {shift}"
            )

    @staticmethod
    def _get_slots(
        employee_ids: Iterable[int], shifts: Iterable[Shift]
    ) -> Iterable[tuple[int, Shift]]:
        for employee_id, shift in product(employee_ids, shifts):
            yield employee_id, shift

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
