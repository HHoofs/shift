from __future__ import annotations

from dataclasses import dataclass

from shift.domain.base import Model


@dataclass(repr=True)
class Employee(Model):
    name: str
    contract_hours: int
    specification_id: int
    events: list = []

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Employee):
            return NotImplemented
        return self.id == other.id
