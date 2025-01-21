from typing import Annotated
from typing import Any
from typing import List
from typing import Optional

from pydantic import BeforeValidator
from pydantic import Field

from armis_sdk.core.base_entity import BaseEntity


def ensure_list_of_ints(value: Any) -> Any:
    if isinstance(value, list):
        return list(map(int, value))

    return None


class Site(BaseEntity):
    # Schema fields
    id: str
    name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    location: Optional[str] = None
    parent_id: Optional[str] = None
    tier: Optional[str] = None
    network_equipment_device_ids: Annotated[
        Optional[List[int]], BeforeValidator(ensure_list_of_ints)
    ] = None

    # Relationship fields
    children: Optional[List["Site"]] = Field(default_factory=list)
