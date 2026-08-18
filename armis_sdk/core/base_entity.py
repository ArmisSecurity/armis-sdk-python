from typing import TypeVar

from pydantic import BaseModel
from pydantic import ConfigDict


class BaseEntity(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        strict=True,
    )


BaseEntityT = TypeVar("BaseEntityT", bound=BaseEntity)
