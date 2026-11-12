from pydantic import Field

from armis_sdk.core.base_entity import BaseEntity
from armis_sdk.entities.asq_rule import AsqRule
from armis_sdk.entities.site import Site


class Boundary(BaseEntity):
    """A `Boundary` is a logical segment in the network."""

    id: int | None = Field(strict=False, default=None)
    """The id of the boundary."""

    name: str | None = None
    """The name of the boundary."""

    asq_rule: AsqRule | None = None
    """The ASQ rule that determines which assets belong to the boundary."""

    site_ids: list[int] | None = None
    """
    The ids of the sites to associate with the boundary.

    This field is only used when creating / updating a boundary.
    """

    sites: list[Site] | None = Field(default=None, frozen=True)
    """
    The sites associated with the boundary.

    This field is read-only, use [`site_ids`][armis_sdk.entities.boundary.Boundary.site_ids]
    to change the associated sites.
    """
