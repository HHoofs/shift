from calendar import Calendar
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Sequence

from ortools.sat.python import cp_model  # type: ignore

from shift.domain.base import Model
from shift.domain.model import EmployeeSlot
from shift.domain.shift import Slot


@dataclass
class ModelDistribution(Model):
    employee_ids: list[int] = field(default_factory=list)

    def add_optimization(
        self,
        slots: Sequence[Slot],
        model: cp_model.CpModel,
        employee_slots: dict[EmployeeSlot, cp_model.IntVar],
    ) -> None:
        n_week_day_slots = defaultdict(list)

        for employee_slot, slot_assigned in employee_slots.items():
            key = (employee_slot[0], employee_slot[1].day.week_day)
            n_week_day_slots[key] = model.NewIntVar(
                0, len(slots), f"<employee: {key[0]}; week day: {key[1]}>"
            )
            n_week_day_slots[key].append(slot_assigned)

        employee_shifts_for_week_day = dict()

        for employee_week_day, _slots in n_week_day_slots.items():
            employee_shifts_for_week_day[employee_week_day] = model.NewIntVar(
                0,
                len(slots),
                f"<employee: {employee_week_day[0]}; "
                f"week day: {employee_week_day[1]}>",
            )
            model.AddMaxEquality(
                employee_shifts_for_week_day[employee_week_day],
                sum(_slots),
            )

        model.Minimize(sum()
            sum(v_x for v_x in var_x.values())
            + sum(-v_m for v_m in var_m.values())
        )
