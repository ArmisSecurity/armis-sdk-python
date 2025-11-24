import datetime
from typing import Literal
from typing import Optional

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

    urls_creation_time: Optional[datetime.datetime] = Field(strict=False)
    """The creation time of the URLs."""
