import datetime
import ipaddress

import pandas

from armis_sdk.entities.data_export.ip_connection import IpConnection


def test_series_to_model():
    series = pandas.Series(
        {
            "host": "example.com",
            "port_dst": 443,
            "transport_protocol": "TCP",
            "protocol": "HTTPS",
            "server_ip": "10.0.0.2",
            "client_ip": "::1",
            "server_router_mac": "00:1a:2b:3c:4d:5e",
            "client_router_mac": "00:1a:2b:3c:4d:5f",
            "is_client_external": False,
            "is_server_external": True,
            "packets_count": 10,
            "outbound_bytes_count": 100,
            "inbound_bytes_count": 200,
            "service_name": "web",
            "event_count": 3,
            "device_id": 1,
            "service_device_id": 2,
            "dt": "2025-11-01",
            "hr": 5,
            "agg_dt": "2025-11-01",
        },
    )

    assert IpConnection.series_to_model(series) == IpConnection(
        host="example.com",
        port_dst=443,
        transport_protocol="TCP",
        protocol="HTTPS",
        server_ip=ipaddress.IPv4Address("10.0.0.2"),
        client_ip=ipaddress.IPv6Address("::1"),
        server_router_mac="00:1a:2b:3c:4d:5e",
        client_router_mac="00:1a:2b:3c:4d:5f",
        is_client_external=False,
        is_server_external=True,
        packets_count=10,
        outbound_bytes_count=100,
        inbound_bytes_count=200,
        service_name="web",
        event_count=3,
        device_id=1,
        service_device_id=2,
        dt=datetime.datetime(2025, 11, 1),
        hr=5,
        agg_dt=datetime.datetime(2025, 11, 1),
    )


def test_series_to_model_empty():
    assert IpConnection.series_to_model(pandas.Series()) == IpConnection()
