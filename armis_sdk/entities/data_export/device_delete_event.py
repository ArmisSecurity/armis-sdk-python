import datetime
from typing import ClassVar
from typing import Self

import pandas

from armis_sdk.entities.data_export.base_exported_entity import BaseExportedEntity


class DeviceDeleteEvent(BaseExportedEntity):
    """
    This class represents a device delete event row that was exported using the data export API.
    """

    entity_name: ClassVar[str] = "device-delete-events"

    device_id: int | None = None
    """The id of the device that was deleted"""

    deleted_timestamp: datetime.datetime | None = None
    """When the device was deleted (UTC)"""

    @classmethod
    def series_to_model(cls, series: pandas.Series) -> Self:
        return cls(
            device_id=cls._value_or_none(series.get("device_id")),
            deleted_timestamp=cls._value_or_none(series.get("deleted_timestamp")),
        )
