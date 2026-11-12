import datetime

import pytest
import pytest_httpx

from armis_sdk.clients.integrations_client import IntegrationsClient
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.entities.integration import Integration
from armis_sdk.entities.integration import IntegrationCycleStatistics
from armis_sdk.entities.integration import IntegrationStatistics


pytest_plugins = ["tests.plugins.auto_setup_plugin"]

RESPONSE = {
    "id": 1,
    "name": "CrowdStrike",
    "instance_name": "mock_instance",
    "params": {"key": "value"},
    "state": "ACTIVE",
    "collector_id": 3,
    "creation_time": "2026-01-01T00:00:00Z",
    "current_state": "IDLE",
    "statistics": {
        "status": "ACTIVE",
        "cycle_statistics": [{"entity_type": "devices", "sent_to_armis_amount": 5}],
    },
}
EXPECTED = Integration(
    id=1,
    name="CrowdStrike",
    instance_name="mock_instance",
    params={"key": "value"},
    state="ACTIVE",
    collector_id=3,
    creation_time=datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC),
    current_state="IDLE",
    statistics=IntegrationStatistics(
        status="ACTIVE",
        cycle_statistics=[IntegrationCycleStatistics(entity_type="devices", sent_to_armis_amount=5)],
    ),
)


async def test_create(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/integrations",
        method="POST",
        match_json={
            "name": "CrowdStrike",
            "instance_name": "mock_instance",
            "params": {"key": "value"},
            "collector_id": 3,
        },
        json=RESPONSE,
        status_code=201,
    )

    integration = Integration(
        name="CrowdStrike",
        instance_name="mock_instance",
        params={"key": "value"},
        collector_id=3,
    )
    assert await IntegrationsClient().create(integration) == EXPECTED


@pytest.mark.parametrize(
    ["integration", "message"],
    [
        (Integration(id=1, name="a", instance_name="b", params={}), "already has an id"),
        (Integration(instance_name="b", params={}), "without a name"),
        (Integration(name="a", params={}), "without an instance name"),
        (Integration(name="a", instance_name="b"), "without params"),
    ],
)
async def test_create_invalid(httpx_mock: pytest_httpx.HTTPXMock, integration: Integration, message: str):
    httpx_mock.reset()

    with pytest.raises(ArmisError, match=message):
        await IntegrationsClient().create(integration)


async def test_delete(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/integrations/1",
        method="DELETE",
        status_code=204,
    )

    await IntegrationsClient().delete(Integration(id=1))


async def test_delete_without_id(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    with pytest.raises(ArmisError, match="without an id"):
        await IntegrationsClient().delete(Integration())


async def test_get(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(url="https://api.armis.com/v3/settings/integrations/1", json=RESPONSE)

    assert await IntegrationsClient().get(1) == EXPECTED


async def test_list(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/integrations?limit=100",
        json={"items": [RESPONSE], "next": None},
    )

    assert [integration async for integration in IntegrationsClient().list()] == [EXPECTED]


async def test_search(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/integrations/_search",
        method="POST",
        match_json={"filter": {"names": ["CrowdStrike"], "states": ["ACTIVE"]}, "limit": 100},
        json={"items": [RESPONSE], "next": None},
    )

    client = IntegrationsClient()
    results = [item async for item in client.search(names=["CrowdStrike"], states=["ACTIVE"])]
    assert results == [EXPECTED]


async def test_search_without_criteria(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    with pytest.raises(ArmisError, match="At least one"):
        _ = [item async for item in IntegrationsClient().search()]


async def test_update(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/integrations/1",
        method="PATCH",
        match_json={"state": "INACTIVE"},
        json={**RESPONSE, "state": "INACTIVE"},
    )

    result = await IntegrationsClient().update(Integration(id=1, state="INACTIVE"))
    assert result.state == "INACTIVE"


async def test_update_without_id(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    with pytest.raises(ArmisError, match="without an id"):
        await IntegrationsClient().update(Integration(state="INACTIVE"))


async def test_update_nothing(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    integration = Integration(id=1)
    assert await IntegrationsClient().update(integration) is integration
