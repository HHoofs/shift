from dataclasses import dataclass
from enum import Enum

from shift.domain.model import DomainModel


class Block(Enum):
    morning = 1
    evening = 2


@dataclass(frozen=True, eq=True)
class Shift(DomainModel):
    block: Block

    def __repr__(self) -> str:
        return self.block.name

    def __lt__(self, other):
        return self.block.value < other.block.value
