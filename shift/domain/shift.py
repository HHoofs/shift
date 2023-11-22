from dataclasses import dataclass

from shift.domain.model import DomainModel


@dataclass(frozen=True, eq=True)
class Shift(DomainModel):
    part: int
