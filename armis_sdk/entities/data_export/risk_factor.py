from __future__ import annotations

import datetime
import json
from typing import ClassVar
from typing import Optional
from typing import TYPE_CHECKING

from pydantic import BaseModel

from armis_sdk.entities.data_export.base_exported_entity import BaseExportedEntity


if TYPE_CHECKING:
    import pandas


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

    device_id: int | None = None
    """The id of the device with the risk factor"""

    category: str | None = None
    """
    The category of the risk factor

    **Example**: `BEHAVIOURAL`
    """

    type: str | None = None
    """
    The type of the risk factor

    **Example**: `SMBV1_SUPPORT`
    """

    description: str | None = None
    """
    The description of the risk factor

    **Example**: `Device Supports SMBv1`
    """

    score: int | None = None
    """The score of the risk factor"""

    group: str | None = None
    """
    The group of the risk factor

    **Example**: `INSECURE_TRAFFIC_AND_BEHAVIOR`
    """

    remediation_type: str | None = None
    """
    The type of the remediation

    **Example**: `Disable SMBv1 Protocol`
    """

    remediation_description: str | None = None
    """
    The description of the remediation

    **Example**: `Disable support for the SMBv1 protocol on devices where it is not required
    for compatibility reasons. Ensure that alternative, more secure network protocols
    such as SMBv3 are implemented to maintain secure network communications.`
    """

    remediation_recommended_actions: list[RiskFactorRecommendedAction] | None = None
    """The remediation recommended actions"""

    first_seen: datetime.datetime | None = None
    """When the risk factor was first seen on the device"""

    last_seen: datetime.datetime | None = None
    """When the risk factor was last seen on the device"""

    status: str | None = None
    """
    The status of the risk factor in relation to the device

    **Example**: `OPEN`
    """

    status_update_time: datetime.datetime | None = None
    """When was the status last changed"""

    status_updated_by_user_id: int | None = None
    """Which used id last changed the status"""

    status_update_reason: str | None = None
    """
    The reason for the status change

    **Example**: `Matching criteria met again`
    """

    @classmethod
    def series_to_model(cls, series: pandas.Series) -> RiskFactor:
        remediation_recommended_actions = series.get("remediation_recommended_actions")
        return RiskFactor(
            device_id=cls._value_or_none(series.get("device_id")),
            category=cls._value_or_none(series.get("category")),
            type=cls._value_or_none(series.get("type")),
            description=cls._value_or_none(series.get("description")),
            score=(int(score) if (score := cls._value_or_none(series.get("score"))) else None),
            status=cls._value_or_none(series.get("status")),
            group=cls._value_or_none(series.get("group")),
            remediation_type=cls._value_or_none(series.get("remediation")),
            remediation_description=cls._value_or_none(series.get("remediation_description")),
            remediation_recommended_actions=(
                [
                    RiskFactorRecommendedAction(**item)
                    for item in json.loads(remediation_recommended_actions)
                ]
                if isinstance(remediation_recommended_actions, str)
                else None
            ),
            first_seen=cls._value_or_none(series.get("first_seen")),
            last_seen=cls._value_or_none(series.get("last_seen")),
            status_update_time=cls._value_or_none(series.get("status_update_time")),
            status_updated_by_user_id=cls._value_or_none(series.get("status_updated_by_user_id")),
            status_update_reason=cls._value_or_none(series.get("status_update_reason")),
        )
