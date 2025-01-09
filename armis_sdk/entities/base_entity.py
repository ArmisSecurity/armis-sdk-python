from typing import TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic import alias_generators


class BaseEntity(BaseModel):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
        strict=True,
    )


BaseEntityType = TypeVar("BaseEntityType", bound=BaseEntity)
