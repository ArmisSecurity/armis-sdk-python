from typing import List, Optional, AsyncIterator

from pydantic import Field

from armis_sdk.core.armis_client import ArmisClient
from armis_sdk.entities.base_entity import BaseEntity


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


class SitesSdk(ArmisClient):
    async def list(self) -> AsyncIterator[Site]:
        return self.paginate("/api/v1/sites/", "sites", Site)

    async def hierarchy(self) -> List[Site]:
        id_to_site = {site.id: site async for site in await self.list()}
        root = []
        for site in id_to_site.values():
            if parent := id_to_site.get(site.parent_id):
                parent.children.append(site)
            else:
                root.append(site)

        return root
