from typing import Iterable
from ortools.sat.python import cp_model

from shift.domain.day import Day
from shift.domain.shift import Shift
from shift.domain.worker import Worker
from shift.services.scheduler.models import ConstraintModel, create_key


class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(
        self,
        vars,
        workers: Iterable[Worker],
        shifts: Iterable[Shift],
        days: Iterable[Day],
        limit: int = 5,
    ):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._vars = vars
        self._workers = workers
        self._days = days
        self._shifts = shifts
        self._solution_count = 0
        self._solution_limit = limit

    @classmethod
    def from_model(cls, model: ConstraintModel):
        return cls(model._vars, model._workers, model._shifts, model._days)

    def on_solution_callback(self):
        self._solution_count += 1
        print(f"Solution {self._solution_count}")
        for day in self._days:
            print(f"Day {day.day}")
            for worker in self._workers:
                is_working = False
                for shift in self._shifts:
                    if self.Value(self._vars[create_key(day, worker, shift)]):
                        is_working = True
                        print(f"  Worker {worker.name} works shift {shift.part}")
                if not is_working:
                    print(f"  Worker {worker.name} does not work")
        if self._solution_count >= self._solution_limit:
            print(f"Stop search after {self._solution_limit} solutions")
            self.StopSearch()

    @property
    def solution_count(self):
        return self._solution_count
