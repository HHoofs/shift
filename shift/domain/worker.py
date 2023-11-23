from dataclasses import dataclass
from typing import Optional, Sequence

from shift.domain.model import DomainModel
from shift.domain.preference import Preference


@dataclass(frozen=True, eq=True)
class Worker(DomainModel):
    id: int
    name: str
    contract_hours: int
    preferences: Optional[Sequence[Preference]] = None

    def __repr__(self) -> str:
        return self.name
