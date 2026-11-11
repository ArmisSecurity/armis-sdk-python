import datetime
import ipaddress
from typing import Any
from typing import Literal

from pydantic import Field
from pydantic import field_validator

from armis_sdk.core.base_entity import BaseEntity


class Collector(BaseEntity):
    """
    The `Collector` entity represents an Armis collector (physical, virtual, application or broker).
    """

    collector_number: int
    """The number that uniquely identifies the collector."""

    name: str
    """The name of the collector."""

    status: (
        Literal[
            "Active",
            "Collector Received",
            "Critical",
            "Inactive",
            "Initializing",
            "In Shipping",
            "Offline",
            "Pending activation",
            "Warning",
        ]
        | None
    ) = None
    """The status of the collector."""

    type: Literal["Application", "Broker", "Physical", "Unknown", "Virtual"] | None = None
    """The type of the collector."""

    ip_address: ipaddress.IPv4Address | None = Field(strict=False, default=None)
    """The IP address of the collector."""

    mac_address: str | None = None
    """The MAC address of the collector."""

    subnet: ipaddress.IPv4Network | None = Field(strict=False, default=None)
    """
    The default IPv4 subnet of the collector.

    Example: `10.0.0.0/24`
    """

    default_gateway: ipaddress.IPv4Address | None = Field(strict=False, default=None)
    """The default gateway of the collector."""

    last_seen: datetime.datetime | None = Field(strict=False, default=None)
    """When the collector was last seen."""

    cluster_id: int | None = None
    """The id of the cluster the collector belongs to."""

    https_proxy_redacted: str | None = None
    """The (redacted) HTTPS proxy configured on the collector."""

    system_vendor: str | None = None
    """The system vendor of the machine running the collector."""

    k8s_namespace: str | None = None
    """The Kubernetes namespace of the collector."""

    serial_number: str | None = None
    """The serial number of the collector."""

    source_deployment_type: str | None = None
    """
    The deployment type of the collector.

    Example: `DEPLOYMENT_TYPE_OVA`
    """

    collector_runtime: str | None = None
    """
    The runtime of the collector.

    Example: `COLLECTOR_RUNTIME_HOST`
    """

    last_boot_time: datetime.datetime | None = Field(strict=False, default=None)
    """When the collector was last booted."""

    creation_date: datetime.datetime | None = Field(strict=False, default=None)
    """When the collector was created."""

    tracking_number: str | None = None
    """The shipping tracking number of the collector."""

    order_status_update: datetime.datetime | None = Field(strict=False, default=None)
    """When the order status of the collector was last updated."""

    configui_password_expiry_date: datetime.datetime | None = Field(strict=False, default=None)
    """When the password of the collector's configuration UI expires."""

    application_version: str | None = None
    """The version of the collector's application."""

    application_update: Literal["Automatic", "Disabled", "Manual"] | None = None
    """The update mode of the collector's application."""

    @field_validator("subnet", mode="before")
    @classmethod
    def normalize_subnet(cls, value: Any) -> Any:
        # The collector reports its own CIDR, which may include host bits (e.g. `10.0.0.5/24`)
        return ipaddress.IPv4Network(value, strict=False) if isinstance(value, str) else value
