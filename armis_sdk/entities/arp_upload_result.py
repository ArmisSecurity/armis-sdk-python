import datetime

from pydantic import Field

from armis_sdk.core.base_entity import BaseEntity


class ArpUploadResult(BaseEntity):
    """A summary of an accepted ARP records upload."""

    total_rows: int
    """The number of data rows in the file. Blank rows are not counted."""

    accepted_records: int
    """The number of ARP records that were sent for processing."""

    duplicate_rows: int
    """The number of rows that repeated an earlier IP / MAC match and were skipped."""

    expiration: datetime.datetime = Field(strict=False)
    """When the uploaded records expire."""
