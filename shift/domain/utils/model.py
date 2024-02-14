from dataclasses import dataclass, field


@dataclass(frozen=False)
class Model:
    id: int = field(init=False)

    @property
    def entity(self):
        return type(self).__name__
