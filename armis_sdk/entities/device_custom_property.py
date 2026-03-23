import datetime
from typing import Literal

from pydantic import Field

from armis_sdk.core.base_entity import BaseEntity


class DeviceCustomProperty(BaseEntity):
    id: int | None = None
    """The id of the property."""

    name: str = Field(max_length=40, pattern=r"^[\w_]*$")
    """
    The name of the property.

    Example: `Size`
    """

    description: str | None = Field(max_length=250, default=None)
    """
    The description of the property.

    Example: `The size of the device`
    """

    type: Literal[
        "boolean",
        "enum",
        "externalLink",
        "integer",
        "string",
        "timestamp",
    ]
    """
    The type of the property.

    Example: `enum`
    """

    allowed_values: list[str] | None = None
    """
    The allowed values of the property when the 'type' is 'enum'.

    Example: `["s", "m", "l"]`
    """

    created_by: str | None = Field(max_length=50, default=None)
    """Who / what created the property."""

    creation_time: datetime.datetime | None = Field(strict=False, default=None)
    """The creation time of the property."""
