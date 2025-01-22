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
    """
    The `Site` entity represents a physical location at the customer's environment.
    """

    id: str
    """The id of the site."""

    name: Optional[str] = None
    """The name of the site."""

    lat: Optional[float] = None
    """Together with `lng`, represents the physical location of the site on earth."""

    lng: Optional[float] = None
    """Together with `lat`, represents the physical location of the site on earth."""

    location: Optional[str] = None
    """The name of the location of the site, such as an address."""

    parent_id: Optional[str] = None
    """The id of the parent site."""

    tier: Optional[str] = None
    """The tier of the site."""

    network_equipment_device_ids: Annotated[
        Optional[List[int]], BeforeValidator(ensure_list_of_ints)
    ] = None
    """The ids of network equipment devices associated with the site."""

    children: Optional[List["Site"]] = Field(default_factory=list)
    """The sub-sites that are directly under this site 
    (their `parent_id` will match this site's `id`)."""
