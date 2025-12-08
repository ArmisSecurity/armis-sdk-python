import datetime
import json
from typing import ClassVar
from typing import Optional

import pandas
from pydantic import BaseModel

from armis_sdk.entities.data_export.base_exported_entity import BaseExportedEntity


class RiskFactorRecommendedAction(BaseModel):
    id: int
    """The id of the recommended action"""

    title: str
    """
    The title of the recommended action

    **Example**: `Patch and Update Systems`
    """

    description: str
    """
    The description of the recommended action

    **Example**: `Regularly update all operating systems and firmware on network devices 
    to the latest versions to reduce the potential for exploitation of vulnerabilities 
    via obsolete protocols.`
    """

    type: str
    """
    The type of the recommended action

    **Example**: `Mitigation`
    """


class RiskFactor(BaseExportedEntity):
    """
    This class represents a risk factor row that was exported using the data export API.
    """

    entity_name: ClassVar[str] = "risk-factors"

    device_id: int
    """The id of the device with the risk factor"""

    category: str
    """
    The category of the risk factor

    **Example**: `BEHAVIOURAL`
    """

    type: str
    """
    The type of the risk factor

    **Example**: `SMBV1_SUPPORT`
    """

    description: str
    """
    The description of the risk factor

    **Example**: `Device Supports SMBv1`
    """

    score: int
    """The score of the risk factor"""

    group: str
    """
    The group of the risk factor

    **Example**: `INSECURE_TRAFFIC_AND_BEHAVIOR`
    """

    remediation_type: str
    """
    The type of the remediation

    **Example**: `Disable SMBv1 Protocol`
    """

    remediation_description: str
    """
    The description of the remediation

    **Example**: `Disable support for the SMBv1 protocol on devices where it is not required
    for compatibility reasons. Ensure that alternative, more secure network protocols
    such as SMBv3 are implemented to maintain secure network communications.`
    """

    remediation_recommended_actions: list[RiskFactorRecommendedAction]
    """The remediation recommended actions"""

    first_seen: datetime.datetime
    """When the risk factor was first seen on the device"""

    last_seen: datetime.datetime
    """When the risk factor was last seen on the device"""

    status: str
    """
    The status of the risk factor in relation to the device

    **Example**: `OPEN`
    """

    status_update_time: Optional[datetime.datetime]
    """When was the status last changed"""

    status_updated_by_user_id: Optional[int]
    """Which used id last changed the status"""

    status_update_reason: Optional[str]
    """
    The reason for the status change

    **Example**: `Matching criteria met again`
    """

    @classmethod
    def series_to_model(cls, series: pandas.Series) -> "RiskFactor":
        return RiskFactor(
            device_id=series.loc["device_id"],
            category=series.loc["category"],
            type=series.loc["type"],
            description=series.loc["description"],
            score=series.loc["score"],
            status=series.loc["status"],
            group=series.loc["group"],
            remediation_type=series.loc["remidiation"],
            remediation_description=series.loc["remidiation_description"],
            remediation_recommended_actions=[
                RiskFactorRecommendedAction(**item)
                for item in json.loads(series.loc["remoidiation_recommended_actions"])
            ],
            first_seen=series.loc["first_seen"].to_pydatetime(),
            last_seen=series.loc["last_seen"].to_pydatetime(),
            status_update_time=cls._value_or_none(series.loc["status_update_time"]),
            status_updated_by_user_id=cls._value_or_none(
                series.loc["status_updated_by_user_id"]
            ),
            status_update_reason=cls._value_or_none(series.loc["status_update_reason"]),
        )
