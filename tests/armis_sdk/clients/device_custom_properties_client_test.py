import datetime

import pytest
import pytest_httpx

from armis_sdk.clients.device_custom_properties_client import (
    DeviceCustomPropertiesClient,
)
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.entities.device_custom_property import DeviceCustomProperty

pytest_plugins = ["tests.plugins.auto_setup_plugin"]


async def test_create(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/device-custom-properties",
        method="POST",
        match_json={
            "name": "mock_name",
            "description": "mock_description",
            "type": "enum",
            "allowed_values": ["a", "b", "c"],
        },
        json={
            "id": 1,
            "name": "mock_name",
            "description": "mock_description",
            "type": "enum",
            "allowed_values": ["a", "b", "c"],
            "created_by": "mock_created_by",
            "creation_time": "2025-11-20T00:00:00",
        },
    )

    client = DeviceCustomPropertiesClient()
    property_to_create = DeviceCustomProperty(
        name="mock_name",
        description="mock_description",
        type="enum",
        allowed_values=["a", "b", "c"],
    )

    created_property = await client.create(property_to_create)

    assert created_property == DeviceCustomProperty(
        id=1,
        name="mock_name",
        description="mock_description",
        type="enum",
        allowed_values=["a", "b", "c"],
        created_by="mock_created_by",
        creation_time=datetime.datetime(2025, 11, 20),
    )


async def test_create_with_id(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    client = DeviceCustomPropertiesClient()
    property_ = DeviceCustomProperty(id=1, name="mock_name", type="string")

    with pytest.raises(
        ArmisError,
        match=(
            r"Can't create a property that already has an id. "
            r"Did you mean to call `\.update\(property_\)`?"
        ),
    ):
        await client.create(property_)


async def test_delete(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/device-custom-properties/1",
        method="DELETE",
    )

    client = DeviceCustomPropertiesClient()
    property_ = DeviceCustomProperty(id=1, name="mock_name", type="string")

    await client.delete(property_)


async def test_delete_without_id(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    client = DeviceCustomPropertiesClient()
    property_ = DeviceCustomProperty(name="mock_name", type="string")

    with pytest.raises(ArmisError, match=r"Can't delete a property without an id."):
        await client.delete(property_)


async def test_get(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/device-custom-properties/1",
        method="GET",
        json={
            "id": 1,
            "name": "mock_name",
            "description": "mock_description",
            "type": "enum",
            "allowed_values": ["a", "b", "c"],
            "created_by": "mock_created_by",
            "creation_time": "2025-11-20T00:00:00",
        },
    )

    client = DeviceCustomPropertiesClient()

    property_ = await client.get(1)

    assert property_ == DeviceCustomProperty(
        id=1,
        name="mock_name",
        description="mock_description",
        type="enum",
        allowed_values=["a", "b", "c"],
        created_by="mock_created_by",
        creation_time=datetime.datetime(2025, 11, 20),
    )


@pytest.mark.parametrize(
    ["from_response", "expected"],
    [
        pytest.param(
            {
                "id": 1,
                "name": "mock_name1",
                "type": "string",
                "created_by": "mock_created_by1",
                "creation_time": "2025-11-20T00:00:00",
            },
            DeviceCustomProperty(
                id=1,
                name="mock_name1",
                type="string",
                created_by="mock_created_by1",
                creation_time=datetime.datetime(2025, 11, 20),
            ),
            id="Only mandatory fields",
        ),
        pytest.param(
            {
                "id": 2,
                "name": "mock_name2",
                "description": "mock_description2",
                "type": "enum",
                "allowed_values": ["a", "b", "c"],
                "created_by": "mock_created_by2",
                "creation_time": "2025-11-20T00:00:00",
            },
            DeviceCustomProperty(
                id=2,
                name="mock_name2",
                description="mock_description2",
                type="enum",
                allowed_values=["a", "b", "c"],
                created_by="mock_created_by2",
                creation_time=datetime.datetime(2025, 11, 20),
            ),
            id="All fields",
        ),
    ],
)
async def test_list_properties(
    from_response, expected, httpx_mock: pytest_httpx.HTTPXMock
):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/device-custom-properties",
        method="GET",
        json={"items": [from_response]},
    )

    client = DeviceCustomPropertiesClient()
    properties = [property_ async for property_ in client.list()]

    assert properties == [expected]


async def test_update(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/device-custom-properties/1",
        method="PATCH",
        match_json={"description": "new_description"},
        json={
            "id": 1,
            "name": "mock_name",
            "description": "new_description",
            "type": "string",
        },
    )

    client = DeviceCustomPropertiesClient()
    property_ = DeviceCustomProperty(
        id=1, name="mock_name", type="string", description="new_description"
    )

    updated_property = await client.update(property_)
    assert updated_property == DeviceCustomProperty(
        id=1,
        name="mock_name",
        description="new_description",
        type="string",
    )


async def test_update_with_nothing_to_change(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    client = DeviceCustomPropertiesClient()
    property_ = DeviceCustomProperty(id=1, name="mock_name", type="string")

    updated_property = await client.update(property_)

    assert updated_property == property_


async def test_update_without_id(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    client = DeviceCustomPropertiesClient()
    property_ = DeviceCustomProperty(name="mock_name", type="string")

    with pytest.raises(
        ArmisError,
        match=(
            r"Can't update a property without an id. "
            r"Did you mean to call `\.create\(property_\)`?"
        ),
    ):
        await client.update(property_)
