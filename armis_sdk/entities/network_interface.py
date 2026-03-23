from armis_sdk.core.base_entity import BaseEntity


class NetworkInterface(BaseEntity):
    # pylint: disable=line-too-long
    """
    A `NetworkInterface` represents a physical network card of a [Device][armis_sdk.entities.device.Device].
    """

    alias: str | None
    """The alias of the interface."""

    brand: str | None
    """The brand of the interface."""

    broadcast_ssid: str | None
    """The last SSID broadcasted by the interface."""

    channels: list[int]
    """The channels that the interface uses to transmit."""

    description: str | None
    """The description of the interface"""

    hidden_broadcast_ssid: bool | None
    """Is the broadcasted SSID hidden."""

    ipv4_address: str | None
    """The last IPv4 address associated with the interface."""

    ipv6_address: str | None
    """The last IPv6 address associated with the interface."""

    last_connected_ssid: str | None
    """The SSID the interface last connected to."""

    mac_address: str | None
    """The MAC address of the interface."""

    name: str | None
    """The name of the interface."""

    type: str | None
    """The type of the interface."""

    vlan: int | None
    """The VLAN of the interface."""
