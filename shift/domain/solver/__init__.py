from dataclasses import dataclass, field
from itertools import product
from typing import Iterable, Optional

from ortools.sat.python import cp_model  # type: ignore

from shift.domain.base import Model
from shift.domain.model import EmployeeSlot, get_key
from shift.domain.shift import Shift
from shift.domain.solver.optimizers import PlanningOptimization


@dataclass
class Solver(Model):
    planning_id: int
    optimization: Optional[PlanningOptimization] = None
    model: cp_model.CpModel = field(default_factory=cp_model.CpModel())
    employee_slots: dict[EmployeeSlot, cp_model.IntVar] = field(
        default_factory=dict
    )

    def add_slots(
        self, employee_ids: Iterable[int], shifts: Iterable[Shift]
    ) -> None:
        for employee_id, shift in product(employee_ids, shifts):
            self.employee_slots[
                get_key(employee_id, shift)
            ] = self.model.NewBoolVar(
                f"Slot <Employee: {employee_id}; Shift: {shift}"
            )
