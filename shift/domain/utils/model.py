from dataclasses import Field, dataclass, field, fields
from typing import Tuple


@dataclass(frozen=False)
class Model:
    id: int = field(init=False)

    @property
    def entity(self):
        return type(self).__name__

    def __repr__(self) -> str:
        cls_fields: Tuple[Field, ...] = fields(self.__class__)

        for _field in cls_fields:
            # This check is to avoid fields annotated with other types
            # such as `str`
            if _field:
                print(_field)
