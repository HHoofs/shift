from dataclasses import dataclass


@dataclass(frozen=True)
class DomainModel:
    id: int

    @property
    def domain(self):
        return type(self).__name__
