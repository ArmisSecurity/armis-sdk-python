import datetime

from armis_sdk.core.base_entity import BaseEntity
from armis_sdk.enums.collector_image_type import CollectorImageType
from pydantic import Field


class CollectorImage(BaseEntity):
    """
    An entity that represents the details required to download and run a collector image.
    """

    image_type: CollectorImageType = Field(strict=False)
    """The type of the image."""

    image_password: str
    """The password for the OS that is encapsulated by the image."""

    url: str
    """The temporary, presigned URL from which the OS image file can be downloaded."""

    url_expiration_date: datetime.datetime = Field(strict=False)
    """Expiration date of the URL."""
