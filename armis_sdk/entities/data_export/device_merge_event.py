import datetime
from typing import ClassVar
from typing import Self

import pandas

from armis_sdk.entities.data_export.base_exported_entity import BaseExportedEntity


class DeviceMergeEvent(BaseExportedEntity):
    """
    This class represents a device merge event row that was exported using the data export API.
    """

    entity_name: ClassVar[str] = "device-merge-events"

    original_device_id: int | None = None
    """The id of the device that was merged into another device"""

    merge_timestamp: datetime.datetime | None = None
    """When the devices were merged (UTC)"""

    current_active_device_id: int | None = None
    """The id of the device that is currently active after the merge"""

    @classmethod
    def series_to_model(cls, series: pandas.Series) -> Self:
        return cls(
            original_device_id=cls._value_or_none(series.get("original_device_id")),
            merge_timestamp=cls._value_or_none(series.get("merge_timestamp")),
            current_active_device_id=cls._value_or_none(series.get("current_active_device_id")),
        )
