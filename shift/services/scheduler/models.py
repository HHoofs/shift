from itertools import product
from typing import Iterable

from ortools.sat.python import cp_model

from shift.domain.employee import Employee
from shift.domain.shift import Day, Period
from shift.services.scheduler.constraints import (
    shifts_per_day,
    subsequent_days,
    subsequent_shifts,
    subsequent_weeks,
    workers_per_shift,
)
from shift.services.scheduler.distribution import n_shifts, n_shifts_month
from shift.services.scheduler.utils import create_key


class ConstraintModel:
    def __init__(
        self,
        workers: Iterable[Employee],
        shifts: Iterable[Period],
        days: Iterable[Day],
    ) -> None:
        self._workers = workers
        self._shifts = shifts
        self._days = days
        self._model = cp_model.CpModel()
        self._vars = {}

    @property
    def model(self) -> cp_model.CpModel:
        return self._model

    def add_vars_to_model(self):
        for var in self._create_vars(self._workers, self._shifts, self._days):
            self._vars[var] = self.model.NewBoolVar("var" + str(var))

    def add_constraints_to_model(self):
        workers_per_shift(
            self.model, self._vars, self._workers, 1, self._shifts, self._days
        )
        shifts_per_day(
            self.model, self._vars, self._shifts, 1, self._days, self._workers
        )
        subsequent_shifts(
            self.model,
            self._vars,
            self._days,
            [self._shifts[-1]],
            [
                (day, next_day)
                for day, next_day in zip(range(1, 8), list(range(2, 8)) + [1])
            ],
            workers=self._workers,
        )
        subsequent_shifts(
            self.model,
            self._vars,
            self._days,
            self._shifts,
            [
                (day, next_day)
                for day, next_day in zip(range(1, 8), list(range(2, 8)) + [1])
            ],
            workers=self._workers,
        )

        subsequent_days(
            self.model,
            self._vars,
            2,
            self._days,
            [
                (day_0, day_1, day_2)
                for day_0, day_1, day_2 in zip(
                    range(1, 8),
                    list(range(2, 8)) + [1],
                    list(range(3, 8)) + [1, 2],
                )
            ],
            self._workers,
            self._shifts,
        )

        subsequent_days(
            self.model,
            self._vars,
            1,
            self._days,
            [(6, 7)],
            self._workers,
            self._shifts,
        )

        subsequent_weeks(
            self.model,
            self._vars,
            1,
            self._days,
            [(6, 7)],
            self._workers,
            self._shifts,
        )

        subsequent_weeks(
            self.model,
            self._vars,
            1,
            self._days,
            [(1,), (2,), (3,), (4,), (5,)],
            self._workers,
            self._shifts[-1:],
        )

    def add_distribution(self):
        total_working_hours = sum(
            worker.contract_hours for worker in self._workers
        )
        for worker in self._workers:
            n_shifts(
                self.model,
                self._vars,
                worker,
                self._shifts,
                self._days,
                total_working_hours,
                worker.contract_hours,
            )
            n_shifts(
                self.model,
                self._vars,
                worker,
                self._shifts[-1:],
                self._days,
                total_working_hours,
                worker.contract_hours,
            )
            n_shifts(
                self.model,
                self._vars,
                worker,
                self._shifts[-1:],
                [_day for _day in self._days if not _day.week_day < 5],
                total_working_hours,
                worker.contract_hours,
            )
            n_shifts(
                self.model,
                self._vars,
                worker,
                self._shifts,
                [
                    _day
                    for _day in self._days
                    if _day.is_weekend or _day.week_day == 5
                ],
                total_working_hours,
                total_working_hours / len(self._workers),
            )

            n_shifts_month(
                self.model,
                self._vars,
                worker,
                self._shifts,
                self._days,
                total_working_hours,
            )

    def optimize_goal(self):
        var_m = {}
        var_x = {}

        for worker in self._workers:
            var_m[worker] = self.model.NewIntVar(
                -50, 50, "var_m" + str(worker)
            )
            _days = []
            for weekday in range(1, 5):
                _key = worker.name, weekday
                var_x[_key] = self.model.NewBoolVar("var_x" + str(_key))
                self.model.AddMaxEquality(
                    var_x[_key],
                    [
                        self._vars[create_key(worker, shift, day)]
                        for day, shift in product(self._days, self._shifts)
                        if day.week_day == weekday
                    ],
                )
                _days.append(
                    sum(
                        self._vars[create_key(worker, shift, day)]
                        for day, shift in product(self._days, self._shifts)
                        if day.week_day == weekday
                    )
                )

            self.model.AddMaxEquality(var_m[worker], _days)
            self.model.Add(
                sum(var_x[(worker.name, _weekday)] for _weekday in range(1, 5))
                < 4
            )

        self.model.Minimize(
            sum(v_x for v_x in var_x.values())
            + sum(-v_m for v_m in var_m.values())
        )

    @staticmethod
    def _create_vars(
        workers: Iterable[Employee],
        shifts: Iterable[Period],
        rep: Iterable[Day],
    ):
        for var in product(workers, shifts, rep):
            yield create_key(*var)
