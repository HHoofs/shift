from itertools import product
from typing import Iterable

from shift.services.scheduler.models import create_key


def workers_per_shift(model, vars, workers, n, *args: Iterable[tuple]):
    if n != 1:
        raise ValueError(
            f"Planning works only with 1 required worker for each shift. "
            f"It is therefore not possible to plan with the specified "
            f"{n} workers within each shift"
        )
    
    for key in product(*args):
        model.AddExactlyOne(vars[create_key(worker, *key)] for worker in workers)
