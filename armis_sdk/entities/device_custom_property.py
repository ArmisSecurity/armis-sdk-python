import datetime
from typing import Literal
from typing import Optional

from pydantic import Field

from armis_sdk.core.base_entity import BaseEntity


class DeviceCustomProperty(BaseEntity):
    id: Optional[int] = None
    """The id of the property."""

    name: str = Field(max_length=40, pattern=r"^[\w_]*$")
    """
    The name of the property.

    Example: `Size`
    """

    description: Optional[str] = Field(max_length=250, default=None)
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

    allowed_values: Optional[list[str]] = None
    """
    The allowed values of the property when the 'type' is 'enum'.

    Example: `["s", "m", "l"]`
    """

    created_by: Optional[str] = Field(max_length=50, default=None)
    """Who / what created the property."""

    creation_time: Optional[datetime.datetime] = Field(strict=False, default=None)
    """The creation time of the property."""
