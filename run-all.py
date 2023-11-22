from shift.domain.day import Day
from shift.domain.shift import Shift
from shift.domain.worker import Worker
from shift.services.scheduler.models import ConstraintModel
from shift.services.scheduler.optimizers import create_solver
from shift.services.scheduler.results import SolutionCallback


if __name__ == "__main__":
    workers = [Worker(1, "henk"), Worker(2, "ingrid")]
    shifts = [Shift(1, 1), Shift(2, 2)]
    days = [Day(1, 1), Day(1, 2)]
    cm = ConstraintModel(workers, shifts, days)
    cm.add_vars_to_model()
    cm.add_constraints_to_model()
    solutions_callback = SolutionCallback.from_model(cm)
    solver = create_solver()
    solver.Solve(cm.model, solutions_callback)

    # Statistics.
    print("\nStatistics")
    print(f"  - conflicts      : {solver.NumConflicts()}")
    print(f"  - branches       : {solver.NumBranches()}")
    print(f"  - wall time      : {solver.WallTime()} s")
    print(f"  - solutions found: {solutions_callback.solution_count}")