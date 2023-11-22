from ortools.sat.python.cp_model import CpSolver


def create_solver() -> CpSolver:
    solver = CpSolver()
    solver.parameters.linearization_level = 0
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True
    return solver