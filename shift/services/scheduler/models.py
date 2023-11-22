from itertools import product
from typing import Iterable
from ortools.sat.python import cp_model
from shift.domain.day import Day
from shift.domain.shift import Shift
from shift.domain.worker import Worker
from shift.services.scheduler.constraints import workers_per_shift, shifts_per_day
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

    @staticmethod
    def _create_vars(
        workers: Iterable[Worker], shifts: Iterable[Shift], rep: Iterable[Day]
    ):
        for var in product(workers, shifts, rep):
            yield create_key(*var)
