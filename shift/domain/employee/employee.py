from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from shift.domain.utils.model import Model


@dataclass
class Employee(Model):
    name: str
    contract_hours: int
    specification_id: Optional[int] = None

    def __repr__(self) -> str:
        return self.name
