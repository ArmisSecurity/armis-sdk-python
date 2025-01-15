from typing import List, Optional

from pydantic import Field

from armis_sdk.core.base_entity import BaseEntity


class Site(BaseEntity):
    # Schema fields
    id: str
    name: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    location: Optional[str] = None
    parent_id: Optional[str] = None
    tier: Optional[str] = None
    network_equipment_device_ids: Optional[List[str]] = Field(default_factory=list)

    # Relationship fields
    children: Optional[List["Site"]] = Field(default_factory=list)
