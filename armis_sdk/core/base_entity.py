from typing import TypeVar

from pydantic import alias_generators
from pydantic import BaseModel
from pydantic import ConfigDict


class BaseEntity(BaseModel):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
        strict=True,
    )


BaseEntityT = TypeVar("BaseEntityT", bound=BaseEntity)
