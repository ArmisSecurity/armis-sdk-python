import datetime
from typing import ClassVar
from typing import Literal
from typing import Optional

from pydantic import Field

from armis_sdk.entities.asset import Asset
from armis_sdk.entities.boundary import Boundary
from armis_sdk.entities.network_interface import NetworkInterface
from armis_sdk.entities.site import Site


class Device(Asset):
    # pylint: disable=line-too-long
    asset_type: ClassVar[Literal["DEVICE"]] = "DEVICE"

    boundaries: Optional[list[Boundary]] = None
    """The list of boundaries the device belongs to."""

    brand: Optional[str] = None
    """
    The device brand.
    
    Example: `Apple`
    """

    category: Optional[str] = None
    """
    The device category.
    
    Example: `Handheld`
    """

    device_id: Optional[int] = None
    """The unique identifier given to the device by thr Armis engine."""

    display: Optional[str] = None
    """
    The display text of the device.
    
    Example: `My iPhone`
    """

    first_seen: Optional[datetime.datetime] = Field(strict=False, default=None)
    """When was the device first seen."""

    ipv4_addresses: Optional[list[str]] = None
    """The list of IPv4 addresses of the device"""

    ipv6_addresses: Optional[list[str]] = None
    """The list of IPv6 addresses of the device"""

    last_seen: Optional[datetime.datetime] = Field(strict=False, default=None)
    """When was the device last seen."""

    mac_addresses: Optional[list[str]] = None
    """The list of MAC addresses of the device"""

    model: Optional[str] = None
    """
    The model of the device.
    
    Example: `iPhone 17`
    """

    names: Optional[list[str]] = None
    """
    List of names of the device
    
    Example: `["My iPhone 17", "Jane's iPhone"]`
    """

    network_interfaces: Optional[list[NetworkInterface]] = None
    """List of network interfaces detected on the device."""

    os_name: Optional[str] = None
    """
    The OS name running on the device.
    
    Example: `iOS`
    """

    os_version: Optional[str] = None
    """
    The OS version running on the device.

    Example: `17`
    """

    purdue_level: Optional[float] = None
    """
    The purdue level of the devices. See [Wikipedia](https://en.wikipedia.org/wiki/Purdue_Enterprise_Reference_Architecture) article for more details.
    
    Example: `4`
    """

    risk_level: Optional[int] = Field(ge=0, le=1000, default=None)
    """The risk level given to the device by the Armis engine, between `0` and `100`."""

    serial_numbers: Optional[list[str]] = None
    """The list of serial numbers of the device"""

    site: Optional[Site] = None
    """The site in which this device was last seen."""

    tags: Optional[list[str]] = None
    """The tags given to the devices."""

    type: Optional[str] = None
    """
    The type of the device.
    
    Example: `Mobile Phones`
    """

    visibility: Optional[Literal["Full", "Limited"]] = None
    """Whether the device is fully visibly or limited."""
