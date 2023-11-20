from typing import Iterable


def workers_per_shift(model, vars, workers, n, *args: Iterable[tuple]):
    if n != 1:
        raise ValueError(
            f"Planning works only with 1 required worker for each shift. "
            f"It is therefore not possible to plan with the specified "
            f"{n} workers within each shift"
        )

    def set_n_per_shift(key, *_args):
        for _arg in _args[0]:
            key = (*key, _arg)
            if _args[1:]:
                set_n_per_shift(key, _args[1:])
            model.AddExactlyOne(vars[create_key(worker.id, *key)] for worker in workers)

    set_n_per_shift(tuple(), *args)
