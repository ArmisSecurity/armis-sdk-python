import datetime
from typing import Literal

from pydantic import BaseModel
from pydantic import Field


class DataExport(BaseModel):
    """
    The `DataExport` entity represents the data export of an entity.
    """

    enabled: bool
    """Whether the entity is enabled or not for data export."""

    file_format: Literal["parquet"] = "parquet"
    """
    The file format of the URLs.

    Currently the only supported format is `parquet`.
    """

    urls: list[str]
    """URLs to the files that contain the exported data."""

    urls_creation_time: datetime.datetime | None = Field(strict=False)
    """The creation time of the URLs."""

    source_data_timestamp: datetime.datetime | None = Field(strict=False, default=None)
    """
    When the exported data was last refreshed at the source.

    Differs from [`urls_creation_time`][armis_sdk.entities.data_export.data_export.DataExport.urls_creation_time],
    which is when the export files themselves were produced.
    """
