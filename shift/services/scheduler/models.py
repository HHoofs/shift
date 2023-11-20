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
            Repeat(repetition, repetition) for repetition in repetitions
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

    @staticmethod
    def _create_vars(
        workers: Iterable[Worker], shifts: Iterable[Shift], rep: Iterable[Repeat]
    ):
        for worker in workers:
            for shift in shifts:
                for r in rep:
                    yield (worker.id, shift.id, r)


def create_key(*vars: Iterable[DomainModel]):
    key = []
    for var in vars:
        key.append((var.id, var))


if __name__ == "__main__":
    workers = [Worker(1, "henk"), Worker(2, "ingrid")]
    shifts = [Shift(1, 1, 1), Shift(2, 1, 2), Shift(3, 2, 1), Shift(3, 2, 2)]
    cm = ConstraintModel(workers, shifts, 1)
    cm.add_vars_to_model()
    cm.add_constraints_to_model()
