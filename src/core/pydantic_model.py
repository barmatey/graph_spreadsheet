from uuid import UUID

from pydantic import BaseModel


class Model(BaseModel):
    uuid: UUID

    def __hash__(self) -> int:
        return self.uuid.__hash__()
