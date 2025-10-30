import pytest
import pytest_httpx

from armis_sdk.clients.sites_client import SitesClient
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.entities.asq_rule import AsqRule
from armis_sdk.entities.site import Site

pytest_plugins = ["tests.plugins.auto_setup_plugin"]


async def test_create(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/sites",
        method="POST",
        match_json={
            "name": "mock_site",
            "location": "mock_location",
            "parent_id": 2,
            "network_equipment_device_ids": [1, 2, 3],
            "integration_ids": [4, 5, 6],
        },
        json={
            "id": "1",
            "name": "mock_site",
            "location": "mock_location",
            "parent_id": 2,
            "network_equipment_device_ids": [1, 2, 3],
            "integration_ids": [4, 5, 6],
        },
    )

    site_to_create = Site(
        name="mock_site",
        location="mock_location",
        parent_id=2,
        network_equipment_device_ids=[1, 2, 3],
        integration_ids=[4, 5, 6],
    )

    sites_client = SitesClient()
    created_site = await sites_client.create(site_to_create)

    assert created_site == Site(
        id=1,
        name="mock_site",
        location="mock_location",
        parent_id=2,
        network_equipment_device_ids=[1, 2, 3],
        integration_ids=[4, 5, 6],
    )


async def test_create_with_id(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    sites_client = SitesClient()
    site = Site(id=1, name="mock_site", location="mock_location")
    with pytest.raises(
        ArmisError,
        match=(
            r"Can't create a site that already has an id. "
            r"Did you mean to call `\.update\(site\)`?"
        ),
    ):
        await sites_client.create(site)


async def test_create_without_name(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    sites_client = SitesClient()
    site = Site()
    with pytest.raises(ArmisError, match=r"Can't create a site without a name."):
        await sites_client.create(site)


async def test_delete(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/sites/1", method="DELETE"
    )

    site = Site(id=1)
    sites_client = SitesClient()

    await sites_client.delete(site)


async def test_delete_without_id(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    site = Site()
    sites_client = SitesClient()

    with pytest.raises(ArmisError, match=r"Can't delete a site without an id."):
        await sites_client.delete(site)


async def test_get(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/sites/1",
        method="GET",
        json={
            "id": "1",
            "name": "mock_site_1",
            "ruleAql": '{"or": ["asq1", "asq2"]}',
            "network_equipment_device_ids": ["1", "2", "3"],
            "integration_ids": ["4", "5", "6"],
        },
    )

    sites_client = SitesClient()
    site = await sites_client.get("1")

    assert site == Site(
        id=1,
        name="mock_site_1",
        asq_rule=AsqRule(or_=["asq1", "asq2"]),
        network_equipment_device_ids=[1, 2, 3],
        integration_ids=[4, 5, 6],
    )


async def test_hierarchy(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/sites?limit=1000",
        method="GET",
        json={
            "items": [
                {"id": "1", "name": "mock_site_1"},
                {"id": "2", "name": "mock_site_2", "parent_id": "1"},
                {"id": "3", "name": "mock_site_3", "parent_id": "1"},
                {"id": "4", "name": "mock_site_4", "parent_id": "2"},
                {"id": "5", "name": "mock_site_5"},
                {"id": "6", "name": "mock_site_6", "parent_id": "5"},
                {"id": "7", "name": "mock_site_7", "parent_id": "999"},
            ],
        },
    )
    sites_client = SitesClient()
    hierarchy = await sites_client.hierarchy()

    assert hierarchy == [
        Site(
            id=1,
            name="mock_site_1",
            children=[
                Site(
                    id=2,
                    name="mock_site_2",
                    parent_id=1,
                    children=[
                        Site(
                            id=4,
                            name="mock_site_4",
                            parent_id=2,
                        )
                    ],
                ),
                Site(
                    id=3,
                    name="mock_site_3",
                    parent_id=1,
                ),
            ],
        ),
        Site(
            id=5,
            name="mock_site_5",
            children=[
                Site(
                    id=6,
                    name="mock_site_6",
                    parent_id=5,
                )
            ],
        ),
        Site(
            id=7,
            name="mock_site_7",
            parent_id=999,
            children=[],
        ),
    ]


@pytest.mark.parametrize(
    ["from_response", "expected"],
    [
        pytest.param(
            {"id": "1", "name": "mock_site_1"},
            Site(
                id=1,
                name="mock_site_1",
            ),
            id="Only mandatory fields",
        ),
        pytest.param(
            {
                "id": "2",
                "name": "mock_site_2",
                "lat": 1.23,
                "lng": 4.56,
                "location": "mock_location",
                "parent_id": "1",
                "tier": "mock_tier",
                "integration_ids": ["4", "5", "6"],
                "network_equipment_device_ids": ["7", "8", "9"],
            },
            Site(
                id=2,
                name="mock_site_2",
                lat=1.23,
                lng=4.56,
                location="mock_location",
                parent_id=1,
                tier="mock_tier",
                integration_ids=[4, 5, 6],
                network_equipment_device_ids=[7, 8, 9],
            ),
            id="All fields",
        ),
    ],
)
async def test_list_sites(from_response, expected, httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/sites?limit=1000",
        method="GET",
        json={"items": [from_response]},
    )

    sites_client = SitesClient()
    sites = [site async for site in sites_client.list()]

    assert sites == [expected]


async def test_list_sites_with_multiple_pages(
    monkeypatch, httpx_mock: pytest_httpx.HTTPXMock
):
    monkeypatch.setenv("ARMIS_PAGE_SIZE", "2")
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/sites?limit=2",
        method="GET",
        json={
            "next": 2,
            "items": [
                {"id": "1", "name": "mock_site_1"},
                {"id": "2", "name": "mock_site_2"},
            ],
        },
    )
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/sites?after=2&limit=2",
        method="GET",
        json={
            "next": 4,
            "items": [
                {"id": "3", "name": "mock_site_3"},
                {"id": "4", "name": "mock_site_4"},
            ],
        },
    )
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/sites?after=4&limit=2",
        method="GET",
        json={
            "next": None,
            "items": [
                {"id": "5", "name": "mock_site_5"},
            ],
        },
    )

    sites_client = SitesClient()
    sites = [site async for site in sites_client.list()]

    assert sites == [
        Site(id=1, name="mock_site_1"),
        Site(id=2, name="mock_site_2"),
        Site(id=3, name="mock_site_3"),
        Site(id=4, name="mock_site_4"),
        Site(id=5, name="mock_site_5"),
    ]


async def test_update_with_nothing_to_change(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()
    sites_client = SitesClient()
    site = Site(id=1)

    updated_site = await sites_client.update(site)
    assert updated_site == site


async def test_update_simple_properties(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/settings/sites/1",
        method="PATCH",
        match_json={"name": "new_name", "location": "new location", "parent_id": 2},
        json={
            "id": 1,
            "name": "new_name",
            "location": "new location",
            "parent_id": 2,
        },
    )

    sites_client = SitesClient()
    site = Site(id=1, name="new_name", location="new location", parent_id=2)

    updated_site = await sites_client.update(site)
    assert updated_site == Site(
        id=1, name="new_name", location="new location", parent_id=2
    )


async def test_update_without_id(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()

    sites_client = SitesClient()
    site = Site(name="mock_site", location="mock_location")
    with pytest.raises(
        ArmisError,
        match=r"Can't update a site without an id. Did you mean to call `\.create\(site\)`?",
    ):
        await sites_client.update(site)
