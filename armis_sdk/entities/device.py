from __future__ import annotations

import datetime  # noqa: TC003
from typing import ClassVar
from typing import Literal

from pydantic import Field

from armis_sdk.entities.asset import Asset
from armis_sdk.entities.boundary import Boundary
from armis_sdk.entities.network_interface import NetworkInterface
from armis_sdk.entities.site import Site


class Device(Asset):
    asset_type: ClassVar[Literal["DEVICE"]] = "DEVICE"

    boundaries: list[Boundary] | None = None
    """The list of boundaries the device belongs to."""

    brand: str | None = None
    """
    The device brand.

    Example: `Apple`
    """

    category: str | None = None
    """
    The device category.

    Example: `Handheld`
    """

    device_id: int | None = None
    """The unique identifier given to the device by thr Armis engine."""

    display: str | None = None
    """
    The display text of the device.

    Example: `My iPhone`
    """

    first_seen: datetime.datetime | None = Field(strict=False, default=None)
    """When was the device first seen."""

    ipv4_addresses: list[str] | None = None
    """The list of IPv4 addresses of the device"""

    ipv6_addresses: list[str] | None = None
    """The list of IPv6 addresses of the device"""

    last_seen: datetime.datetime | None = Field(strict=False, default=None)
    """When was the device last seen."""

    mac_addresses: list[str] | None = None
    """The list of MAC addresses of the device"""

    model: str | None = None
    """
    The model of the device.

    Example: `iPhone 17`
    """

    names: list[str] | None = None
    """
    List of names of the device

    Example: `["My iPhone 17", "Jane's iPhone"]`
    """

    network_interfaces: list[NetworkInterface] | None = None
    """List of network interfaces detected on the device."""

    os_name: str | None = None
    """
    The OS name running on the device.

    Example: `iOS`
    """

    os_version: str | None = None
    """
    The OS version running on the device.

    Example: `17`
    """

    purdue_level: float | None = None
    """
    The purdue level of the devices. See [Wikipedia](https://en.wikipedia.org/wiki/Purdue_Enterprise_Reference_Architecture) article for more details.

    Example: `4`
    """

    risk_level: int | None = Field(ge=0, le=1000, default=None)
    """The risk level given to the device by the Armis engine, between `0` and `100`."""

    serial_numbers: list[str] | None = None
    """The list of serial numbers of the device"""

    site: Site | None = None
    """The site in which this device was last seen."""

    tags: list[str] | None = None
    """The tags given to the devices."""

    type: str | None = None
    """
    The type of the device.

    Example: `Mobile Phones`
    """

    visibility: Literal["Full", "Limited"] | None = None
    """Whether the device is fully visibly or limited."""


Device.model_rebuild()
