import pytest
import pytest_httpx

from armis_sdk.clients.site_integrations_client import SiteIntegrationsClient
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.entities.site import Site

pytest_plugins = ["tests.plugins.setup_plugin"]


@pytest.mark.usefixtures("setup_env_variables", "authorized")
async def test_update(httpx_mock: pytest_httpx.HTTPXMock):
    # List current ids
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/1/integrations-ids/",
        method="GET",
        json={"data": {"integrationIds": [1, 2, 3, 4]}},
    )

    # Add new ids
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/1/integrations-ids/",
        method="POST",
        match_json={"integrationId": 5},
    )
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/1/integrations-ids/",
        method="POST",
        match_json={"integrationId": 6},
    )

    # Remove old ids
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/1/integrations-ids/1/",
        method="DELETE",
    )
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/1/integrations-ids/3/",
        method="DELETE",
    )

    site_integrations_client = SiteIntegrationsClient()

    site = Site(id=1, name="mock_site", integration_ids=[2, 4, 5, 6])

    await site_integrations_client.update(site)


@pytest.mark.usefixtures("setup_env_variables")
async def test_update_with_no_integrations_set():
    site = Site(id=1, name="mock_site")
    site_integrations_client = SiteIntegrationsClient()

    with pytest.raises(ArmisError, match="The property 'integration_ids' must be set."):
        await site_integrations_client.update(site)
