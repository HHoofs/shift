from typing import Iterable

from shift.domain.model import DomainModel


def create_key(*vars: Iterable[DomainModel]):
    sorted_keys = sorted(vars, key=lambda var: var.domain)
    generated_keys = [f"{var.domain}-{var.id}" for var in sorted_keys]
    cp_key = "|".join(generated_keys)
    return cp_key
