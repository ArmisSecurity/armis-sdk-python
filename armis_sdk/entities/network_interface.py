from typing import Optional

from armis_sdk.core.base_entity import BaseEntity


class NetworkInterface(BaseEntity):
    # pylint: disable=line-too-long
    """
    A `NetworkInterface` represents a physical network card of a [Device][armis_sdk.entities.device.Device].
    """

    alias: Optional[str]
    """The alias of the interface."""

    brand: Optional[str]
    """The brand of the interface."""

    broadcast_ssid: Optional[str]
    """The last SSID broadcasted by the interface."""

    channels: list[int]
    """The channels that the interface uses to transmit."""

    description: Optional[str]
    """The description of the interface"""

    hidden_broadcast_ssid: Optional[bool]
    """Is the broadcasted SSID hidden."""

    ipv4_address: Optional[str]
    """The last IPv4 address associated with the interface."""

    ipv6_address: Optional[str]
    """The last IPv6 address associated with the interface."""

    last_connected_ssid: Optional[str]
    """The SSID the interface last connected to."""

    mac_address: Optional[str]
    """The MAC address of the interface."""

    name: Optional[str]
    """The name of the interface."""

    type: Optional[str]
    """The type of the interface."""

    vlan: Optional[int]
    """The VLAN of the interface."""
