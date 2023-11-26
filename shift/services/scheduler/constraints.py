from itertools import product
import itertools
from typing import Iterable, Mapping, Tuple
from shift.domain.day import Day, WeekDay
from shift.domain.model import DomainModel
from ortools.sat.python import cp_model
from shift.domain.shift import Shift
from shift.domain.worker import Worker

from shift.services.scheduler.utils import create_key

DomainModels = Iterable[Iterable[DomainModel]]


def workers_per_shift(
    model: cp_model.CpModel,
    vars: Mapping[str, cp_model.LinearExprT],
    workers,
    n=1,
    *args: Iterable[DomainModels],
):
    if n != 1:
        raise ValueError(
            f"Planning works only with 1 required worker for each shift. "
            f"It is therefore not possible to plan with the specified "
            f"{n} workers within each shift"
        )

    for key in product(*args):
        model.AddExactlyOne(vars[create_key(worker, *key)] for worker in workers)


def shifts_per_day(
    model: cp_model.CpModel,
    vars: Mapping[str, cp_model.LinearExprT],
    shifts,
    n=1,
    *args: Iterable[DomainModels],
):
    if n != 1:
        raise ValueError(
            f"Planning works only with 1 required worker for each shift. "
            f"It is therefore not possible to plan with the specified "
            f"{n} workers within each shift"
        )

    for key in product(*args):
        model.AddAtMostOne(vars[create_key(shift, *key)] for shift in shifts)


def shifts_on_weekday(
    model: cp_model.CpModel,
    vars: Mapping[str, cp_model.LinearExpr],
    n: int,
    worker: Worker,
    weekday: WeekDay,
    shifts: Iterable[Shift],
    days: Iterable[Day],
):
    _sum = sum(
        vars[create_key(worker, day, shift)]
        for day in days
        for shift in shifts
        if day.weekday == weekday
    )
    model.Add(_sum <= n)


def shift_on_day(
    model: cp_model.CpModel,
    vars: Mapping[str, cp_model.LinearExpr],
    include: bool,
    day: Iterable[Day],
    workers: Iterable[Worker],
    shifts: Iterable[Shift],
):
    for worker in workers:
        _vars = (vars[create_key(worker, day, shift)] for shift in shifts)
        if include:
            model.AddExactlyOne(_vars)
        else:
            model.Add(sum(_vars) <= 0)


def subsequent_shifts(
    model: cp_model.CpModel,
    vars: Mapping[str, cp_model.LinearExprT],
    days: Iterable[Day],
    shifts: Iterable[Shift],
    weekdays: Iterable[Tuple[WeekDay, WeekDay]],
    workers: Iterable[Worker],
):
    for subsequent_days in _consecutive_days(weekdays, days):
        for worker in workers:
            model.AddAtMostOne(
                vars[create_key(worker, _day, _shift)]
                for (_day, _shift) in zip(subsequent_days, (max(shifts), min(shifts)))
            )


def subsequent_days(
    model: cp_model.CpModel,
    vars: Mapping[str, cp_model.LinearExprT],
    n: int,
    days: Iterable[Day],
    weekdays: Iterable[Tuple[WeekDay, WeekDay]],
    workers: Iterable[Worker],
    shifts: Iterable[Shift],
):
    for _days in _consecutive_days(weekdays, days):
        for worker in workers:
            _sum = sum(
                vars[create_key(worker, _day, _shift)]
                for (_day, _shift) in product(_days, shifts)
            )
            model.Add(_sum <= n)


def _consecutive_days(
    weekdays: Iterable[Tuple[WeekDay, ...]], days: Iterable[Day]
) -> Iterable[Tuple[Day, ...]]:
    n_weekdays = {len(_weekdays) for _weekdays in weekdays}
    if len(n_weekdays) > 1:
        raise ValueError("All sets of weekdays should have the same length")
    weekdays = [sorted(_weekday) for _weekday in weekdays]

    n = n_weekdays.pop()
    for days_inclusive in _tee(sorted(days), n):
        if list(day.weekday for day in days_inclusive) in weekdays:
            yield days_inclusive


def _tee(days: Iterable[Day], n: int = 2) -> Iterable[Tuple[Day, ...]]:
    days_tee = itertools.tee(days, n)
    for i in range(1, n):
        for _ in range(i):
            next(days_tee[i], None)
    return zip(*days_tee)
