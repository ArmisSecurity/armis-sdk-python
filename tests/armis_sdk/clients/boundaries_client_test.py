import pytest
import pytest_httpx

from armis_sdk.clients.boundaries_client import BoundariesClient
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.entities.asq_rule import AsqRule
from armis_sdk.entities.boundary import Boundary
from armis_sdk.entities.site import Site


pytest_plugins = ["tests.plugins.auto_setup_plugin"]

RESPONSE = {
    "id": 1,
    "name": "mock_boundary",
    "asq_rule": {"or": ["asq1"]},
    "sites": [{"id": 2, "name": "mock_site"}],
}
EXPECTED = Boundary(
    id=1,
    name="mock_boundary",
    asq_rule=AsqRule(or_=["asq1"]),
    sites=[Site(id=2, name="mock_site")],
)


async def test_create(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/boundaries",
        method="POST",
        match_json={"name": "mock_boundary", "asq_rule": {"or": ["asq1"]}, "site_ids": [2]},
        json=RESPONSE,
        status_code=201,
    )

    boundary = Boundary(name="mock_boundary", asq_rule=AsqRule(or_=["asq1"]), site_ids=[2])
    assert await BoundariesClient().create(boundary) == EXPECTED


async def test_create_with_id(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    with pytest.raises(ArmisError, match="already has an id"):
        await BoundariesClient().create(Boundary(id=1, name="mock_boundary"))


async def test_create_without_name(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    with pytest.raises(ArmisError, match="without a name"):
        await BoundariesClient().create(Boundary())


async def test_delete(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/boundaries/1",
        method="DELETE",
        status_code=204,
    )

    await BoundariesClient().delete(Boundary(id=1))


async def test_delete_without_id(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    with pytest.raises(ArmisError, match="without an id"):
        await BoundariesClient().delete(Boundary(name="mock_boundary"))


async def test_get(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(url="https://api.armis.com/v3/settings/boundaries/1", json=RESPONSE)

    assert await BoundariesClient().get(1) == EXPECTED


async def test_list(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/boundaries?limit=100",
        json={"items": [RESPONSE], "next": None},
    )

    assert [boundary async for boundary in BoundariesClient().list()] == [EXPECTED]


async def test_update(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/boundaries/1",
        method="PATCH",
        match_json={"name": "mock_boundary"},
        json=RESPONSE,
    )

    assert await BoundariesClient().update(Boundary(id=1, name="mock_boundary")) == EXPECTED


async def test_update_without_id(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    with pytest.raises(ArmisError, match="without an id"):
        await BoundariesClient().update(Boundary(name="mock_boundary"))


async def test_update_nothing(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    boundary = Boundary(id=1)
    assert await BoundariesClient().update(boundary) is boundary
