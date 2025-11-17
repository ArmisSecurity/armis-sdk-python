import datetime
from typing import ClassVar
from typing import Optional

import pandas

from armis_sdk.entities.data_export.base_exported_entity import BaseExportedEntity


class Application(BaseExportedEntity):
    """
    This class represents an application row that was exported using the data export API.
    """

    entity_name: ClassVar[str] = "applications"

    device_id: int
    """The id of the device with the application"""

    vendor: str
    """
    The vendor of the application

    **Example**: `Google`
    """

    name: str
    """
    The name of the application

    **Example**: `Chrome`
    """

    version: str
    """
    The version of the application

    **Example**: `30.0.1599.40`
    """

    cpe: Optional[str]
    """
    The CPE (Common Platform Enumeration) of the application

    **Example**: `cpe:2.3:a:google:chrome:30.0.1599.40:*:*:*:*:*:*:*`
    """

    first_seen: datetime.datetime
    """When the application was first seen on the device"""

    last_seen: datetime.datetime
    """When the application was last seen on the device"""

    @classmethod
    def series_to_model(cls, series: pandas.Series) -> "Application":
        return Application(
            device_id=series.loc["device_id"],
            vendor=series.loc["vendor"],
            name=series.loc["name"],
            version=series.loc["version"],
            cpe=cls._value_or_none(
                series.loc["cpe"] if "cpe" in series.index else None
            ),
            first_seen=series.loc["first_seen"].to_pydatetime(),
            last_seen=series["last_seen"].to_pydatetime(),
        )
