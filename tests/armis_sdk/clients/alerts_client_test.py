import datetime
import ipaddress

import pytest_httpx

from armis_sdk.clients.alerts_client import AlertsClient
from armis_sdk.entities.alert import Alert
from armis_sdk.entities.alert import DeviceEndpoint
from armis_sdk.entities.alert import HostEndpoint
from armis_sdk.entities.alert import IpAddressEndpoint
from armis_sdk.entities.mitre_attack_label import MitreAttackLabel


pytest_plugins = ["tests.plugins.auto_setup_plugin"]


async def test_get(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/alerts/42",
        json={
            "id": 42,
            "severity": "HIGH",
            "type": "SYSTEM_POLICY_VIOLATION",
            "status": "OPEN",
            "activity_timestamp": "2026-05-13T08:30:00Z",
            "title": "mock_title",
            "classification": "Security > Threat",
            "policy_id": 88,
            "affected_devices_count": 1,
            "mitre_attack_labels": [{"matrix": "ENTERPRISE", "tactic": "Initial Access", "technique": "Phishing"}],
            "activity_uuids": ["uuid1"],
            "device_ids": [1],
            "connection_ids": [2],
            "source_endpoints": [{"id": 1, "name": "device", "ipv4_addresses": ["10.0.0.1"]}],
            "destination_endpoints": [
                {"id": "10.0.0.2", "name": "10.0.0.2", "ipv4_address": "10.0.0.2"},
                {"id": "example.com", "name": "Example"},
            ],
        },
    )

    alert = await AlertsClient().get(42)

    assert alert == Alert(
        id=42,
        severity="HIGH",
        type="SYSTEM_POLICY_VIOLATION",
        status="OPEN",
        activity_timestamp=datetime.datetime(2026, 5, 13, 8, 30, tzinfo=datetime.UTC),
        title="mock_title",
        classification="Security > Threat",
        policy_id=88,
        affected_devices_count=1,
        mitre_attack_labels=[MitreAttackLabel(matrix="ENTERPRISE", tactic="Initial Access", technique="Phishing")],
        activity_uuids=["uuid1"],
        device_ids=[1],
        connection_ids=[2],
        source_endpoints=[DeviceEndpoint(id=1, name="device", ipv4_addresses=[ipaddress.IPv4Address("10.0.0.1")])],
        destination_endpoints=[
            IpAddressEndpoint(id="10.0.0.2", name="10.0.0.2", ipv4_address=ipaddress.IPv4Address("10.0.0.2")),
            HostEndpoint(id="example.com", name="Example"),
        ],
    )
