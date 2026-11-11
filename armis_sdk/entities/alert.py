import datetime
import ipaddress
from typing import Annotated
from typing import Literal

from pydantic import Field

from armis_sdk.core.base_entity import BaseEntity
from armis_sdk.entities.mitre_attack_label import MitreAttackLabel


class DeviceEndpoint(BaseEntity):
    """
    A device that is the source / destination of the activity of an [Alert][armis_sdk.entities.alert.Alert].

    Used in [`source_endpoints`][armis_sdk.entities.alert.Alert.source_endpoints] and
    [`destination_endpoints`][armis_sdk.entities.alert.Alert.destination_endpoints].
    """

    id: int
    """The id of the device."""

    name: str
    """The name of the device."""

    ipv4_addresses: list[Annotated[ipaddress.IPv4Address, Field(strict=False)]] | None = None
    """The IPv4 addresses of the device at the time of the alert."""

    mac_addresses: list[str] | None = None
    """The MAC addresses observed on the device."""

    risk_level: int | str | None = None
    """The overall risk score of the device (or a mask string)."""

    business_impact: str | None = None
    """
    The business impact of the device.

    Example: `HIGH`
    """

    data_sources: list[str] | None = None
    """The data sources of the device."""

    boundary_names: list[str] | None = None
    """The names of the boundaries the device belongs to."""

    site_name: str | None = None
    """The name of the site the device belongs to."""


class IpAddressEndpoint(BaseEntity):
    """
    An IP address that is the source / destination of the activity of an [Alert][armis_sdk.entities.alert.Alert].

    Used in [`source_endpoints`][armis_sdk.entities.alert.Alert.source_endpoints] and
    [`destination_endpoints`][armis_sdk.entities.alert.Alert.destination_endpoints].
    """

    id: str
    """The IP address, serving as the identifier."""

    name: str
    """The display name of the IP address."""

    ipv4_address: ipaddress.IPv4Address = Field(strict=False)
    """The IPv4 address."""


class HostEndpoint(BaseEntity):
    """
    A host name that is the source / destination of the activity of an [Alert][armis_sdk.entities.alert.Alert].

    Used in [`source_endpoints`][armis_sdk.entities.alert.Alert.source_endpoints] and
    [`destination_endpoints`][armis_sdk.entities.alert.Alert.destination_endpoints].
    """

    id: str
    """The host name, serving as the identifier."""

    name: str
    """The display name of the host."""


class Alert(BaseEntity):
    """
    The `Alert` entity represents a security alert raised by Armis.
    """

    id: int
    """The id of the alert."""

    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    """The severity of the alert."""

    type: Literal["ANOMALY_DETECTION", "SYSTEM_POLICY_VIOLATION", "USER_POLICY_VIOLATION"]
    """How the alert was raised."""

    status: Literal["IGNORED", "OPEN", "RESOLVED", "SUPPRESSED", "UNHANDLED"]
    """The current triage state of the alert."""

    activity_timestamp: datetime.datetime = Field(strict=False)
    """When the activity that triggered the alert was observed."""

    title: str
    """
    The headline of the alert.

    Example: `Suspicious outbound connection from manufacturing printer`
    """

    affected_devices_count: int
    """The number of distinct devices implicated in the alert."""

    classification: str | None = None
    """
    The name of the alert's classification.

    Example: `Security > Threat`
    """

    policy_id: int | None = None
    """The id of the policy that raised the alert."""

    description: str | None = None
    """The long-form description of the alert."""

    status_change_time: datetime.datetime | None = Field(strict=False, default=None)
    """When the status of the alert last changed."""

    last_alert_update_time: datetime.datetime | None = Field(strict=False, default=None)
    """When the alert was last enriched / updated."""

    mitre_attack_labels: list[MitreAttackLabel] = Field(default_factory=list)
    """The MITRE ATT&CK annotations of the alert."""

    activity_uuids: list[str] = Field(default_factory=list)
    """The UUIDs of the activities that contributed to the alert."""

    device_ids: list[int] = Field(default_factory=list)
    """The ids of the devices implicated in the alert."""

    connection_ids: list[int] = Field(default_factory=list)
    """The ids of the connections implicated in the alert."""

    source_endpoints: list[DeviceEndpoint | IpAddressEndpoint | HostEndpoint] = Field(default_factory=list)
    """The source endpoints of the activities that triggered the alert."""

    destination_endpoints: list[DeviceEndpoint | IpAddressEndpoint | HostEndpoint] = Field(default_factory=list)
    """The destination endpoints of the activities that triggered the alert."""
