from collections import defaultdict
from itertools import product
from math import ceil, floor
from typing import Iterable
from ortools.sat.python import cp_model
from shift.domain.day import Day
from shift.domain.shift import Shift
from shift.domain.worker import Worker
from shift.services.scheduler.constraints import (
    subsequent_shifts,
    workers_per_shift,
    shifts_per_day,
)
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
            self._model, self._vars, self._workers, 1, self._shifts, self._days
        )
        shifts_per_day(
            self._model, self._vars, self._shifts, 1, self._days, self._workers
        )
        subsequent_shifts(
            self._model,
            self._vars,
            self._days,
            [self._shifts[-1]],
            [
                (day, next_day)
                for day, next_day in zip(range(1, 7), list(range(2, 7)) + [1])
            ],
            workers=self._workers,
        )
        subsequent_shifts(
            self._model,
            self._vars,
            self._days,
            self._shifts,
            [
                (day, next_day)
                for day, next_day in zip(range(1, 8), list(range(2, 8)) + [1])
            ],
            workers=self._workers,
        )

    def add_distribution(self):
        total_working_hours = sum(worker.contract_hours for worker in self._workers)
        total_shifts = len(self._days) * len(self._shifts)
        for worker in self._workers:
            n_shifts = worker.contract_hours / total_working_hours * total_shifts
            if n_shifts.is_integer():
                min_shifts, max_shifts = int(n_shifts), int(n_shifts)
            else:
                min_shifts, max_shifts = floor(n_shifts), ceil(n_shifts)
            worker_shifts = [
                self._vars[create_key(worker, _shift, _day)]
                for _shift, _day in product(self._shifts, self._days)
            ]
            self.model.Add(min_shifts <= sum(worker_shifts))
            self.model.Add(sum(worker_shifts) <= max_shifts)

            worker_late_shifts = [
                self._vars[create_key(worker, self._shifts[-1], _day)]
                for _day in self._days
            ]
            self.model.Add(min_shifts // 2 <= sum(worker_late_shifts))
            self.model.Add(sum(worker_late_shifts) <= max_shifts // 2)

    def optimize_goal(self):
        for worker in self._workers:
            for weekday in range(1, 8):
                for shift in self._shifts:
                    _key = worker.name, weekday, shift.block.value
                    self._varx[_key] = self.model.NewBoolVar("var" + str(_key))
                    self.model.AddMaxEquality(
                        self._varx[_key],
                        [
                            self._vars[create_key(worker, shift, day)]
                            for day in self._days
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
