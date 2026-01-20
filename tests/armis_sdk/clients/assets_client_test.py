import datetime

import pytest
import pytest_httpx

from armis_sdk.clients.assets_client import AssetsClient
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.core.armis_error import BulkUpdateError
from armis_sdk.entities.asset import Asset
from armis_sdk.entities.asset_field_description import AssetFieldDescription
from armis_sdk.entities.device import Device
from tests.armis_sdk.clients import assets_test_data

pytest_plugins = ["tests.plugins.auto_setup_plugin"]


class NotDevice(Asset):
    pass


async def test_list_by_last_seen_datetime(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/assets/_search",
        method="POST",
        match_json={
            "limit": 100,
            "asset_type": "DEVICE",
            "fields": assets_test_data.ALL_DEVICE_FIELDS,
            "filter": {
                "filter_criteria": "LAST_SEEN",
                "last_seen_ge": "2025-12-03T00:00:00",
            },
        },
        json={
            "items": [
                {"asset_id": 1, "fields": assets_test_data.MOCK_DEVICE_FULL_RAW_DATA}
            ]
        },
    )

    assets_client = AssetsClient()
    last_seen = datetime.datetime(2025, 12, 3)
    devices = [
        device async for device in assets_client.list_by_last_seen(Device, last_seen)
    ]

    assert devices == [assets_test_data.MOCK_DEVICE_FULL]


async def test_list_by_last_seen_datetime_explicit_fields(
    httpx_mock: pytest_httpx.HTTPXMock,
):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/assets/_search",
        method="POST",
        match_json={
            "limit": 100,
            "asset_type": "DEVICE",
            "fields": ["brand", "custom.MyField1", "custom.MyField2", "purdue_level"],
            "filter": {
                "filter_criteria": "LAST_SEEN",
                "last_seen_ge": "2025-12-03T00:00:00",
            },
        },
        json={
            "items": [
                {"asset_id": 1, "fields": assets_test_data.MOCK_DEVICE_PARTIAL_RAW_DATA}
            ]
        },
    )

    assets_client = AssetsClient()
    last_seen = datetime.datetime(2025, 12, 3)
    fields = ["brand", "custom.MyField1", "custom.MyField2", "purdue_level"]
    devices = [
        device
        async for device in assets_client.list_by_last_seen(
            Device, last_seen, fields=fields
        )
    ]

    assert devices == [assets_test_data.MOCK_DEVICE_PARTIAL]


async def test_list_by_last_seen_timedelta(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/assets/_search",
        method="POST",
        match_json={
            "limit": 100,
            "asset_type": "DEVICE",
            "fields": assets_test_data.ALL_DEVICE_FIELDS,
            "filter": {"filter_criteria": "LAST_SEEN", "last_seen_seconds": 3600},
        },
        json={
            "items": [
                {"asset_id": 1, "fields": assets_test_data.MOCK_DEVICE_FULL_RAW_DATA}
            ]
        },
    )

    assets_client = AssetsClient()
    last_seen = datetime.timedelta(hours=1)
    devices = [
        device async for device in assets_client.list_by_last_seen(Device, last_seen)
    ]

    assert devices == [assets_test_data.MOCK_DEVICE_FULL]


async def test_list_by_last_seen_timedelta_explicit_fields(
    httpx_mock: pytest_httpx.HTTPXMock,
):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/assets/_search",
        method="POST",
        match_json={
            "limit": 100,
            "asset_type": "DEVICE",
            "fields": ["brand", "custom.MyField1", "custom.MyField2", "purdue_level"],
            "filter": {"filter_criteria": "LAST_SEEN", "last_seen_seconds": 3600},
        },
        json={
            "items": [
                {"asset_id": 1, "fields": assets_test_data.MOCK_DEVICE_PARTIAL_RAW_DATA}
            ]
        },
    )

    assets_client = AssetsClient()
    last_seen = datetime.timedelta(hours=1)
    fields = ["brand", "custom.MyField1", "custom.MyField2", "purdue_level"]
    devices = [
        device
        async for device in assets_client.list_by_last_seen(
            Device, last_seen, fields=fields
        )
    ]

    assert devices == [assets_test_data.MOCK_DEVICE_PARTIAL]


async def test_list_by_last_seen_invalid_fields():
    assets_client = AssetsClient()
    last_seen = datetime.timedelta(hours=1)
    fields = ["device_id", "foo", "bar", "tags"]

    with pytest.raises(
        ArmisError,
        match="The following fields are not supported with this operation: 'foo', 'bar'",
    ):
        async for _ in assets_client.list_by_last_seen(
            Device, last_seen, fields=fields
        ):
            pass


async def test_list_by_asset_id(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/assets/_search",
        method="POST",
        match_json={
            "limit": 100,
            "asset_type": "DEVICE",
            "fields": assets_test_data.ALL_DEVICE_FIELDS,
            "filter": {
                "filter_criteria": "ASSET_ID",
                "asset_id_source": "IPV4_ADDRESS",
                "asset_ids": ["1.1.1.1"],
            },
        },
        json={
            "items": [
                {"asset_id": 1, "fields": assets_test_data.MOCK_DEVICE_FULL_RAW_DATA}
            ]
        },
    )

    assets_client = AssetsClient()
    asset_ids = ["1.1.1.1"]
    devices = [
        device
        async for device in assets_client.list_by_asset_id(
            Device,
            asset_ids,
            asset_id_source="IPV4_ADDRESS",
        )
    ]

    assert devices == [assets_test_data.MOCK_DEVICE_FULL]


async def test_list_by_asset_id_explicit_fields(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/assets/_search",
        method="POST",
        match_json={
            "limit": 100,
            "asset_type": "DEVICE",
            "fields": ["brand", "custom.MyField1", "custom.MyField2", "purdue_level"],
            "filter": {
                "filter_criteria": "ASSET_ID",
                "asset_id_source": "IPV4_ADDRESS",
                "asset_ids": ["1.1.1.1"],
            },
        },
        json={
            "items": [
                {"asset_id": 1, "fields": assets_test_data.MOCK_DEVICE_PARTIAL_RAW_DATA}
            ]
        },
    )

    assets_client = AssetsClient()
    asset_ids = ["1.1.1.1"]
    devices = [
        device
        async for device in assets_client.list_by_asset_id(
            Device,
            asset_ids,
            asset_id_source="IPV4_ADDRESS",
            fields=["brand", "custom.MyField1", "custom.MyField2", "purdue_level"],
        )
    ]

    assert devices == [assets_test_data.MOCK_DEVICE_PARTIAL]


async def test_list_by_asset_id_invalid_fields():
    assets_client = AssetsClient()
    fields = ["device_id", "foo", "bar", "tags"]

    with pytest.raises(
        ArmisError,
        match="The following fields are not supported with this operation: 'foo', 'bar'",
    ):
        async for _ in assets_client.list_by_asset_id(Device, [1, 2, 3], fields=fields):
            pass


async def test_update(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/assets/_bulk",
        method="POST",
        match_json={
            "items": [
                {
                    "asset_id": 1,
                    "key": "custom.MyField1",
                    "operation": "SET",
                    "value": "value1",
                },
                {
                    "asset_id": 1,
                    "key": "custom.MyField2",
                    "operation": "SET",
                    "value": 2,
                },
                {
                    "asset_id": 2,
                    "key": "custom.MyField1",
                    "operation": "SET",
                    "value": "value3",
                },
                {"asset_id": 2, "key": "custom.MyField2", "operation": "UNSET"},
            ],
            "asset_type": "DEVICE",
            "asset_id_source": "ASSET_ID",
        },
        json={"items": [{"status": 202}] * 4},
    )

    assets_client = AssetsClient()

    assets = [
        Device(device_id=1, custom={"MyField1": "value1", "MyField2": 2}),
        Device(device_id=2, custom={"MyField1": "value3"}),
    ]
    fields = ["custom.MyField1", "custom.MyField2"]
    await assets_client.update(assets, fields)


async def test_update_with_asset_id_source(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/assets/_bulk",
        method="POST",
        match_json={
            "items": [
                {
                    "asset_id": "1.1.1.1",
                    "key": "custom.MyField1",
                    "operation": "SET",
                    "value": "value1",
                },
                {
                    "asset_id": "1.1.1.1",
                    "key": "custom.MyField2",
                    "operation": "SET",
                    "value": 2,
                },
                {
                    "asset_id": "2.2.2.2",
                    "key": "custom.MyField1",
                    "operation": "SET",
                    "value": "value3",
                },
                {"asset_id": "2.2.2.2", "key": "custom.MyField2", "operation": "UNSET"},
            ],
            "asset_type": "DEVICE",
            "asset_id_source": "IPV4_ADDRESS",
        },
        json={"items": [{"status": 202}] * 4},
    )

    assets_client = AssetsClient()

    assets = [
        Device(
            ipv4_addresses=["1.1.1.1"], custom={"MyField1": "value1", "MyField2": 2}
        ),
        Device(ipv4_addresses=["2.2.2.2"], custom={"MyField1": "value3"}),
    ]
    fields = ["custom.MyField1", "custom.MyField2"]
    await assets_client.update(assets, fields, asset_id_source="IPV4_ADDRESS")


async def test_update_with_failed_requests(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/assets/_bulk",
        method="POST",
        match_json={
            "items": [
                {
                    "asset_id": 1,
                    "key": "custom.MyField1",
                    "operation": "SET",
                    "value": "value1",
                },
                {
                    "asset_id": 1,
                    "key": "custom.MyField2",
                    "operation": "SET",
                    "value": 2,
                },
                {
                    "asset_id": 2,
                    "key": "custom.MyField1",
                    "operation": "SET",
                    "value": "value3",
                },
                {"asset_id": 2, "key": "custom.MyField2", "operation": "UNSET"},
            ],
            "asset_type": "DEVICE",
            "asset_id_source": "ASSET_ID",
        },
        json={
            "items": [
                {"status": 202},
                {"status": 202},
                {"status": 400, "error": "Bad Request"},
                {"status": 202},
            ]
        },
    )

    assets_client = AssetsClient()

    assets = [
        Device(device_id=1, custom={"MyField1": "value1", "MyField2": 2}),
        Device(device_id=2, custom={"MyField1": "value3"}),
    ]
    fields = ["custom.MyField1", "custom.MyField2"]

    with pytest.raises(
        BulkUpdateError,
        match=(
            "Failed to update item at index 2. "
            'Request: {"asset_id": 2, "key": "custom.MyField1", '
            '"operation": "SET", "value": "value3"}, '
            'Response: {"status": 400, "error": "Bad Request"}'
        ),
    ):
        await assets_client.update(assets, fields)


@pytest.mark.parametrize(
    ["assets", "fields", "expected_error"],
    [
        (
            [Device(), NotDevice()],
            ["custom.MyField"],
            "All assets must be of the same type, got 2 types: 'Device', 'NotDevice'",
        ),
        (
            [Device()],
            ["custom.MyField", "purdue_level"],
            "The following fields are not supported with this operation: 'purdue_level'",
        ),
        ([Device()], ["custom.MyField"], "Device at index 0 doesn't have a device id"),
    ],
)
async def test_update_with_validation_errors(assets, fields, expected_error):
    assets_client = AssetsClient()

    with pytest.raises(ArmisError, match=expected_error):
        await assets_client.update(assets, fields)


async def test_list_fields(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/assets/_search/fields?asset_type=DEVICE",
        method="GET",
        json={
            "items": [
                {"name": "device_id", "type": "integer", "is_list": False},
                {"name": "names", "type": "string", "is_list": True},
                {"name": "custom.Size", "type": "enum", "is_list": False},
                {
                    "name": "integration.qualys_agent_id",
                    "type": "string",
                    "is_list": False,
                },
            ]
        },
    )

    assets_client = AssetsClient()
    fields = [field async for field in assets_client.list_fields(Device)]

    assert fields == [
        AssetFieldDescription(name="device_id", type="integer", is_list=False),
        AssetFieldDescription(name="names", type="string", is_list=True),
        AssetFieldDescription(name="custom.Size", type="enum", is_list=False),
        AssetFieldDescription(
            name="integration.qualys_agent_id", type="string", is_list=False
        ),
    ]
