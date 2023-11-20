from dataclasses import dataclass

from shift.domain.model import DomainModel


@dataclass(frozen=True, eq=True)
class Worker(DomainModel):
    id: int
    name: str
