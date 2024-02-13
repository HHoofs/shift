from dataclasses import dataclass, field
from typing import Sequence

from ortools.sat.python import cp_model  # type: ignore

from shift.domain.shifts.days import WeekDay, WeekDays
from shift.domain.shifts.shift import Slot
from shift.domain.utils.model import Model
from shift.domain.utils.utils import EmployeeSlot, get_key


@dataclass
class PlanningOptimization(Model):
    employee_ids: list[int] = field(default_factory=list)
    week_days: Sequence[WeekDay] = field(default_factory=lambda: WeekDays)

    def add_optimization(
        self,
        slots: Sequence[Slot],
        model: cp_model.CpModel,
        employee_slots: dict[EmployeeSlot, cp_model.IntVar],
    ) -> None:
        any_planned_on_week_day = {}
        max_planned_on_week_day = {}

        for employee_id in self.employee_ids:
            n_planned_on_week_day = []
            max_planned_on_week_day[employee_id] = model.NewIntVar(
                0,
                len(slots),
                f"max planned on week day <employee: {employee_id}>",
            )
            for week_day in self.week_days:
                key = (employee_id, week_day)

                any_planned_on_week_day[key] = model.NewBoolVar(
                    f"any planned <employee: {key[0]}; week day: {key[1]}>"
                )

                _slots = [
                    employee_slots[get_key(employee_id, slot.shift)]
                    for slot in slots
                    if slot.day.week_day == week_day
                ]

                model.AddMaxEquality(
                    any_planned_on_week_day[key],
                    _slots,
                )

                n_planned_on_week_day.append(sum(_slots))

            model.AddMaxEquality(
                max_planned_on_week_day[employee_id], n_planned_on_week_day
            )

        # TODO: Add balance (don't use a single employee to dump)

        model.Minimize(
            sum(
                any_planned for any_planned in any_planned_on_week_day.values()
            )
            + sum(
                -max_planned
                for max_planned in max_planned_on_week_day.values()
            )
        )
