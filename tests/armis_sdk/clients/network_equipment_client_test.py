import pytest
import pytest_httpx

from armis_sdk.clients.network_equipment_client import NetworkEquipmentClient
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.entities.site import Site

pytest_plugins = ["tests.plugins.setup_plugin"]


@pytest.mark.usefixtures("setup_env_variables", "authorized")
async def test_update(httpx_mock: pytest_httpx.HTTPXMock):
    # List current ids
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/1/network-equipment/",
        method="GET",
        json={"data": {"networkEquipmentDeviceIds": [1, 2, 3, 4]}},
    )

    # Add new ids
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/1/network-equipment/_bulk/",
        method="POST",
        match_json={"networkEquipmentDeviceIds": [5, 6]},
    )

    # Remove old ids
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/1/network-equipment/1/",
        method="DELETE",
    )
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/1/network-equipment/3/",
        method="DELETE",
    )

    network_equipment_client = NetworkEquipmentClient()

    site = Site(id="1", name="mock_site", network_equipment_device_ids=[2, 4, 5, 6])

    await network_equipment_client.update(site)


@pytest.mark.usefixtures("setup_env_variables")
async def test_update_with_no_devices_set():
    site = Site(id="1", name="mock_site")
    network_equipment_client = NetworkEquipmentClient()

    with pytest.raises(
        ArmisError, match="The property 'network_equipment_device_ids' must be set."
    ):
        await network_equipment_client.update(site)
