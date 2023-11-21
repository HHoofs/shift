from itertools import product
from typing import Iterable
from ortools.sat.python import cp_model
from shift.domain.model import DomainModel
from shift.domain.repeat import Repeat
from shift.domain.shift import Shift
from shift.domain.worker import Worker
from shift.services.scheduler import constraints


class ConstraintModel:
    def __init__(
        self, workers: Iterable[Worker], shifts: Iterable[Shift], repetitions: int
    ) -> None:
        self._workers = workers
        self._shifts = shifts
        self._reps: Iterable[Repeat] = [
            Repeat(repetition, repetition) for repetition in range(repetitions)
        ]
        self._model = cp_model.CpModel()
        self._vars = {}

    @property
    def model(self) -> cp_model.CpModel:
        return self._model

    def add_vars_to_model(self):
        for var in self._create_vars(self._workers, self._shifts, self._reps):
            self._vars[var] = self.model.NewBoolVar("var" + str(var))

    def add_constraints_to_model(self):
        constraints.workers_per_shift(
            self._model, self._vars, self._workers, 1, self._shifts, self._reps
        )
        constraints.shifts_per_day(
            self._model, self._vars, self._shifts, 1, self._reps, self._workers
        )

    @staticmethod
    def _create_vars(
        workers: Iterable[Worker], shifts: Iterable[Shift], rep: Iterable[Repeat]
    ):
        for var in product(workers, shifts, rep):
            yield create_key(*var)


def create_key(*vars: Iterable[DomainModel]):
    sorted_keys = sorted(vars, key=lambda var: var.domain)
    generated_keys = [f'{var.domain}-{var.id}' for var in sorted_keys]
    cp_key = '|'.join(generated_keys)
    return cp_key


if __name__ == "__main__":
    workers = [Worker(1, "henk"), Worker(2, "ingrid")]
    shifts = [Shift(1, 1, 1), Shift(2, 1, 2), Shift(3, 2, 1), Shift(3, 2, 2)]
    cm = ConstraintModel(workers, shifts, 1)
    cm.add_vars_to_model()
    cm.add_constraints_to_model()
    solv
