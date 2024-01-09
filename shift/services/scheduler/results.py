import csv
from collections import defaultdict
from typing import Iterable

from ortools.sat.python import cp_model

from shift.domain.day import Day
from shift.domain.employee import Employee
from shift.domain.shift import Period
from shift.services.scheduler.models import ConstraintModel, create_key


class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(
        self,
        vars,
        workers: Iterable[Employee],
        shifts: Iterable[Period],
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
        with open("test.csv", "w") as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            worker_shifts = defaultdict(list)
            for day in self._days:
                print(day)
                if day.week_day == 1:
                    if worker_shifts:
                        for worker in self._workers:
                            if worker_shifts[worker.name]:
                                writer.writerow(
                                    [worker.name] + worker_shifts[worker.name]
                                )
                    writer.writerow(
                        [
                            day.date.isocalendar()[1],
                            "Ma",
                            "Di",
                            "Wo",
                            "Do",
                            "Vr",
                            "Za",
                            "Zo",
                        ]
                    )
                    worker_shifts = defaultdict(list)
                for worker in self._workers:
                    worker_planned = ""
                    for shift in self._shifts:
                        if self.Value(
                            self._vars[create_key(day, worker, shift)]
                        ):
                            print(f"  {worker} works {shift} shift")
                            worker_planned = shift
                    worker_shifts[worker.name].append(worker_planned)

        if self._solution_count >= self._solution_limit:
            print(f"Stop search after {self._solution_limit} solutions")
            self.StopSearch()

    @property
    def solution_count(self):
        return self._solution_count
