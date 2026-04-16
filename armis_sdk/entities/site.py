from __future__ import annotations

import json
from typing import Annotated
from typing import Any
from typing import Optional

from pydantic import BeforeValidator
from pydantic import Field
from pydantic import model_validator

from armis_sdk.core.base_entity import BaseEntity
from armis_sdk.entities.asq_rule import AsqRule


def ensure_list_of_ints(value: Any) -> Any:
    if isinstance(value, list):
        return list(map(int, value))

    return None


class Site(BaseEntity):
    """
    The `Site` entity represents a physical location at the customer's environment.
    """

    id: int | None = Field(strict=False, default=None)
    """The id of the site."""

    name: str | None = None
    """The name of the site."""

    lat: float | None = Field(frozen=True, default=None)
    """
    The latitude coordinate of the physical location of the site on earth.

    This field is read-only and is automatically derived from the
    [`location`][armis_sdk.entities.site.Site.location] field.

    Example: `37.7900103`

    """

    lng: float | None = Field(frozen=True, default=None)
    """
    The longitude coordinate of the physical location of the site on earth.

    This field is read-only and is automatically derived from the
    [`location`][armis_sdk.entities.site.Site.location] field.

    Example: `-122.4007818`
    """

    location: str | None = None
    """
    The name of the location of the site, such as an address.

    Example: `548 Market Street Suite 97439 San Francisco, CA 94104-5401`

    When this field is set, the [`lat`][armis_sdk.entities.site.Site.lat] and
    [`lng`][armis_sdk.entities.site.Site.lng] are automatically derived from it.
    """

    parent_id: int | None = Field(strict=False, default=None)
    """The id of the parent site."""

    tier: str | None = None
    """The tier of the site."""

    asq_rule: AsqRule | None = Field(default=None)
    """The ASQ rule of the site."""

    network_equipment_device_ids: Annotated[list[int] | None, BeforeValidator(ensure_list_of_ints)] = None
    """The ids of network equipment devices associated with the site."""

    integration_ids: Annotated[list[int] | None, BeforeValidator(ensure_list_of_ints)] = None
    """The ids of the integration associated with the site."""

    children: list[Site] = Field(default_factory=list)
    """The sub-sites that are directly under this site
    (their `parent_id` will match this site's `id`)."""

    @model_validator(mode="before")
    @classmethod
    def transform_rule_aql_to_asq_rule(cls, data: Any) -> dict:
        if not isinstance(data, dict):
            raise TypeError("Value must be a dict.")
        if "ruleAql" in data:
            data["asq_rule"] = json.loads(data.pop("ruleAql"))
        return data


Site.model_rebuild()
