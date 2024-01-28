from itertools import groupby, product
from math import ceil, floor
from typing import Iterable, Mapping

from ortools.sat.python import cp_model

from shift.domain.day import Day
from shift.services.scheduler.utils import (
    create_key,
)


def n_shifts(
    model: cp_model.CpModel,
    vars: Mapping[str, cp_model.LinearExprT],
    worker,
    shifts,
    days,
    total_hours,
    contract_hours,
    wiggle: int = 0,
):
    total_shifts = len(shifts) * len(days)
    worker_shifts = contract_hours / total_hours * total_shifts

    if worker_shifts.is_integer():
        min_shifts, max_shifts = (
            int(worker_shifts),
            int(worker_shifts),
        )
    else:
        min_shifts, max_shifts = (
            floor(worker_shifts),
            ceil(worker_shifts),
        )
    min_shifts, max_shifts = (
        min_shifts - wiggle,
        max_shifts + wiggle,
    )
    worker_shifts = [
        vars[create_key(worker, _shift, _day)]
        for _shift, _day in product(shifts, days)
    ]
    model.Add(min_shifts <= sum(worker_shifts))
    model.Add(sum(worker_shifts) <= max_shifts)


def n_shifts_month(
    model: cp_model.CpModel,
    vars: Mapping[str, cp_model.LinearExprT],
    worker,
    shifts,
    days: Iterable[Day],
    total_hours,
):
    total_shifts = len(shifts) * len(days)
    months = {_day.date.month for _day in days}
    worker_shifts = worker.contract_hours / total_hours * total_shifts
    worker_monthly_shifts = worker_shifts / len(months)

    if worker_monthly_shifts.is_integer():
        min_shifts, max_shifts = (
            int(worker_monthly_shifts),
            int(worker_monthly_shifts),
        )
    else:
        min_shifts, max_shifts = (
            floor(worker_monthly_shifts),
            ceil(worker_monthly_shifts),
        )
    min_shifts, max_shifts = (
        min_shifts - 1,
        max_shifts + 1,
    )

    for _, _days in groupby(
        days,
        lambda day: day.date.month,
    ):
        month_shifts = [
            vars[
                create_key(
                    worker,
                    _shift,
                    _day,
                )
            ]
            for _shift, _day in product(shifts, _days)
        ]
        model.Add(min_shifts <= sum(month_shifts))
        model.Add(sum(month_shifts) <= max_shifts)
