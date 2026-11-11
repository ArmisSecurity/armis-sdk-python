import datetime
import ipaddress
from typing import ClassVar
from typing import Self

import pandas

from armis_sdk.entities.data_export.base_exported_entity import BaseExportedEntity


class IpConnection(BaseExportedEntity):
    """
    This class represents an (hourly aggregated) IP connection row that was exported using the data export API.
    """

    entity_name: ClassVar[str] = "ip-connections"

    host: str | None = None
    """The host name of the server"""

    port_dst: int | None = None
    """The destination port"""

    transport_protocol: str | None = None
    """
    The transport protocol

    **Example**: `TCP`
    """

    protocol: str | None = None
    """
    The name of the protocol of the destination port

    **Example**: `HTTPS`
    """

    server_ip: ipaddress.IPv4Address | ipaddress.IPv6Address | None = None
    """The IP address of the server"""

    client_ip: ipaddress.IPv4Address | ipaddress.IPv6Address | None = None
    """The IP address of the client"""

    server_router_mac: str | None = None
    """
    The MAC address of the server's router

    **Example**: `00:1a:2b:3c:4d:5e`
    """

    client_router_mac: str | None = None
    """The MAC address of the client's router"""

    is_client_external: bool | None = None
    """Whether the client is external to the network"""

    is_server_external: bool | None = None
    """Whether the server is external to the network"""

    packets_count: int | None = None
    """The number of packets in the connection"""

    outbound_bytes_count: int | None = None
    """The number of outbound bytes in the connection"""

    inbound_bytes_count: int | None = None
    """The number of inbound bytes in the connection"""

    service_name: str | None = None
    """The name of the service"""

    event_count: int | None = None
    """The number of events in the connection"""

    device_id: int | None = None
    """The id of the client device"""

    service_device_id: int | None = None
    """The id of the server (service) device"""

    dt: datetime.datetime | None = None
    """The date of the connection"""

    hr: int | None = None
    """The hour of the day of the connection"""

    agg_dt: datetime.datetime | None = None
    """The date of the aggregation"""

    @classmethod
    def series_to_model(cls, series: pandas.Series) -> Self:
        return cls(
            host=cls._value_or_none(series.get("host")),
            port_dst=cls._value_or_none(series.get("port_dst")),
            transport_protocol=cls._value_or_none(series.get("transport_protocol")),
            protocol=cls._value_or_none(series.get("protocol")),
            server_ip=cls._value_or_none(series.get("server_ip")),
            client_ip=cls._value_or_none(series.get("client_ip")),
            server_router_mac=cls._value_or_none(series.get("server_router_mac")),
            client_router_mac=cls._value_or_none(series.get("client_router_mac")),
            is_client_external=cls._value_or_none(series.get("is_client_external")),
            is_server_external=cls._value_or_none(series.get("is_server_external")),
            packets_count=cls._value_or_none(series.get("packets_count")),
            outbound_bytes_count=cls._value_or_none(series.get("outbound_bytes_count")),
            inbound_bytes_count=cls._value_or_none(series.get("inbound_bytes_count")),
            service_name=cls._value_or_none(series.get("service_name")),
            event_count=cls._value_or_none(series.get("event_count")),
            device_id=cls._value_or_none(series.get("device_id")),
            service_device_id=cls._value_or_none(series.get("service_device_id")),
            dt=cls._value_or_none(series.get("dt")),
            hr=cls._value_or_none(series.get("hr")),
            agg_dt=cls._value_or_none(series.get("agg_dt")),
        )
