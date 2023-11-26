from collections import defaultdict
from itertools import product
from math import ceil, floor
from typing import Iterable
from ortools.sat.python import cp_model
from shift.domain.day import Day
from shift.domain.shift import Shift
from shift.domain.worker import Worker
from shift.services.scheduler.constraints import (
    subsequent_days,
    subsequent_shifts,
    subsequent_weeks,
    workers_per_shift,
    shifts_per_day,
)
from shift.services.scheduler.distribution import n_shifts, n_shifts_month
from shift.services.scheduler.utils import create_key


class ConstraintModel:
    def __init__(
        self, workers: Iterable[Worker], shifts: Iterable[Shift], days: Iterable[Day]
    ) -> None:
        self._workers = workers
        self._shifts = shifts
        self._days = days
        self._model = cp_model.CpModel()
        self._vars = {}
        self._varx = {}

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
                    range(1, 8), list(range(2, 8)) + [1], list(range(3, 8)) + [1, 2]
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
            self.model, self._vars, 1, self._days, (6, 7), self._workers, self._shifts
        )

        subsequent_weeks(
            self.model,
            self._vars,
            1,
            self._days,
            (5,),
            self._workers,
            self._shifts[-1:],
        )

    def add_distribution(self):
        total_working_hours = sum(worker.contract_hours for worker in self._workers)
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
                [_day for _day in self._days if not _day.weekday < 5],
                total_working_hours,
                worker.contract_hours,
            )
            n_shifts(
                self.model,
                self._vars,
                worker,
                self._shifts,
                [_day for _day in self._days if _day.is_weekend or _day.weekday == 5],
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
        # Weekenden niet opeenvolgend
        for worker in self._workers:
            for weekday in range(1, 5):
                _key = worker.name, weekday
                self._varx[_key] = self.model.NewBoolVar("var" + str(_key))
                self.model.AddMaxEquality(
                    self._varx[_key],
                    [
                        self._vars[create_key(worker, shift, day)]
                        for day, shift in product(self._days, self._shifts)
                        if day.weekday == weekday
                    ],
                )

        self.model.Minimize(sum(var_x for var_x in self._varx.values()))

    @staticmethod
    def _create_vars(
        workers: Iterable[Worker], shifts: Iterable[Shift], rep: Iterable[Day]
    ):
        for var in product(workers, shifts, rep):
            yield create_key(*var)
