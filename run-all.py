from datetime import date, timedelta

from shift.domain.day import Day
from shift.domain.employee import Employee
from shift.domain.shift import Block, Period
from shift.services.scheduler.models import ConstraintModel
from shift.services.scheduler.optimizers import create_solver
from shift.services.scheduler.results import SolutionCallback

if __name__ == "__main__":
    workers = [
        Employee(1, "A", 36),
        Employee(2, "B", 36),
        Employee(3, "C", 36),
        Employee(4, "D", 36),
        Employee(5, "E", 32),
        Employee(6, "F", 32),
        Employee(7, "G", 32),
        Employee(8, "H", 32),
        Employee(9, "I", 32),
        Employee(10, "J", 32),
        Employee(11, "K", 28),
        Employee(12, "L", 28),
    ]
    shifts = [Period(1, Block(1)), Period(2, Block(2))]
    start_day = date(2024, 1, 1)
    days = [
        Day(_day, start_day + timedelta(days=_day)) for _day in range(365 // 2)
    ]
    cm = ConstraintModel(workers, shifts, days)
    cm.add_vars_to_model()
    cm.add_constraints_to_model()
    cm.add_distribution()
    cm.optimize_goal()
    solutions_callback = SolutionCallback.from_model(cm)
    solver = create_solver()
    solver.Solve(cm.model, solutions_callback)

    # Statistics.
    print("\nStatistics")
    print(f"  - conflicts      : {solver.NumConflicts()}")
    print(f"  - branches       : {solver.NumBranches()}")
    print(f"  - wall time      : {solver.WallTime()} s")
    print(f"  - solutions found: {solutions_callback.solution_count}")
