import pytest
import pytest_httpx

from armis_sdk.clients.sites_client import SitesClient
from armis_sdk.entities.site import Site

pytest_plugins = ["tests.plugins.auto_setup_plugin"]


async def test_get(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/1/",
        method="GET",
        json={"data": {"id": "1", "name": "mock_site_1"}},
    )

    sites_client = SitesClient()
    site = await sites_client.get("1")

    assert site == Site(id="1", name="mock_site_1")


async def test_hierarchy(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/?from=0&length=100",
        method="GET",
        json={
            "data": {
                "sites": [
                    {"id": "1", "name": "mock_site_1"},
                    {"id": "2", "name": "mock_site_2", "parentId": "1"},
                    {"id": "3", "name": "mock_site_3", "parentId": "1"},
                    {"id": "4", "name": "mock_site_4", "parentId": "2"},
                    {"id": "5", "name": "mock_site_5"},
                    {"id": "6", "name": "mock_site_6", "parentId": "5"},
                    {"id": "7", "name": "mock_site_7", "parentId": "unknown"},
                ]
            }
        },
    )
    sites_client = SitesClient()
    hierarchy = await sites_client.hierarchy()

    assert hierarchy == [
        Site(
            id="1",
            name="mock_site_1",
            children=[
                Site(
                    id="2",
                    name="mock_site_2",
                    parent_id="1",
                    children=[
                        Site(
                            id="4",
                            name="mock_site_4",
                            parent_id="2",
                        )
                    ],
                ),
                Site(
                    id="3",
                    name="mock_site_3",
                    parent_id="1",
                ),
            ],
        ),
        Site(
            id="5",
            name="mock_site_5",
            children=[
                Site(
                    id="6",
                    name="mock_site_6",
                    parent_id="5",
                )
            ],
        ),
        Site(
            id="7",
            name="mock_site_7",
            parent_id="unknown",
            children=[],
        ),
    ]


@pytest.mark.parametrize(
    ["from_response", "expected"],
    [
        pytest.param(
            {"id": "1", "name": "mock_site_1"},
            Site(
                id="1",
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
                "parentId": "1",
                "tier": "mock_tier",
                "networkEquipmentDeviceIds": ["7", "8", "9"],
            },
            Site(
                id="2",
                name="mock_site_2",
                lat=1.23,
                lng=4.56,
                location="mock_location",
                parent_id="1",
                tier="mock_tier",
                network_equipment_device_ids=[7, 8, 9],
            ),
            id="All fields",
        ),
    ],
)
async def test_list_sites(from_response, expected, httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/?from=0&length=100",
        method="GET",
        json={"data": {"sites": [from_response]}},
    )

    sites_client = SitesClient()
    sites = [site async for site in await sites_client.list()]

    assert sites == [expected]


async def test_list_sites_with_multiple_pages(
    monkeypatch, httpx_mock: pytest_httpx.HTTPXMock
):
    monkeypatch.setenv("ARMIS_PAGE_SIZE", "2")
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/?from=0&length=2",
        method="GET",
        json={
            "data": {
                "next": 2,
                "sites": [
                    {"id": "1", "name": "mock_site_1"},
                    {"id": "2", "name": "mock_site_2"},
                ],
            }
        },
    )
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/?from=2&length=2",
        method="GET",
        json={
            "data": {
                "next": 4,
                "sites": [
                    {"id": "3", "name": "mock_site_3"},
                    {"id": "4", "name": "mock_site_4"},
                ],
            }
        },
    )
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/?from=4&length=2",
        method="GET",
        json={
            "data": {
                "next": None,
                "sites": [
                    {"id": "5", "name": "mock_site_5"},
                ],
            }
        },
    )

    sites_client = SitesClient()
    sites = [site async for site in await sites_client.list()]

    assert sites == [
        Site(id="1", name="mock_site_1"),
        Site(id="2", name="mock_site_2"),
        Site(id="3", name="mock_site_3"),
        Site(id="4", name="mock_site_4"),
        Site(id="5", name="mock_site_5"),
    ]


async def test_update_with_nothing_to_change(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.reset()
    sites_client = SitesClient()
    site = Site(id="1")

    await sites_client.update(site)


async def test_update_simple_properties(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/1/",
        method="PATCH",
        match_json={"name": "new_name", "location": "new location"},
    )

    sites_client = SitesClient()
    site = Site(id="1", name="new_name", location="new location")

    await sites_client.update(site)


async def test_update_with_network_equipment_device_ids(
    httpx_mock: pytest_httpx.HTTPXMock,
):
    # List current ids
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/1/network-equipment/",
        method="GET",
        json={"data": {"networkEquipmentDeviceIds": []}},
    )

    # Add new ids
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/1/network-equipment/_bulk/",
        method="POST",
        match_json={"networkEquipmentDeviceIds": [1, 2, 3]},
    )

    sites_client = SitesClient()
    site = Site(id="1", network_equipment_device_ids=[1, 2, 3])

    await sites_client.update(site)
