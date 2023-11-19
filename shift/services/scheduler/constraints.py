def workers_per_shift(model, shifts, workers, n, *args):
    if n != 1:
        raise ValueError('Planning works only with 1 required worker for each shift. '
                         'It is therefore not possible to plan with the specified '
                         f'{n} workers within each shift'                                                                                                   .')

    def set_n_per_shift(key, *args):
        if not args:
            model.AddExactlyOne(shifts[(worker.name, *key)] for worker in workers)
        key = (*key, args[0])
        set_n_per_shift(key, args[1:])
    
    set_n_per_shift(tuple(), *vars)