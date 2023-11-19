from typing import Iterable
from ortools.sat.python import cp_model


class ConstrainModel:
    def __init__(
        self, workers: Iterable[Worker], shifts: Iterable[Shifts], rep: int
    ) -> None:
        self._workers = workers
        self._shifts = shifts
        self._rep = rep
        self._model = cp_model.CpModel()
        self._vars = {}

    @property
    def model(self) -> cp_model.CpModel:
        return self._model

    def add_vars_to_model(self):
        for var in self._create_vars(self._workers, self._shifts, self._rep):
            self._vars[var] = self.model.NewBoolVar('var' + str(var))

    def add_constraints_to_model(self):
        for shift in self.shift


    @staticmethod
    def _create_vars(workers: Iterable[Worker], shifts: Iterable[Shifts], rep: int):
        for worker in workers:
            for shift in shifts:
                for r in range(rep):

                    yield (worker.name, shift.name, r)
