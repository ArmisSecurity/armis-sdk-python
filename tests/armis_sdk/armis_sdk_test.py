import pytest

from armis_sdk import ArmisSdk
from armis_sdk.clients.data_export_client import DataExportClient
from armis_sdk.clients.sites_client import SitesClient
from armis_sdk.core.armis_client import ArmisClient

pytest_plugins = ["tests.plugins.setup_plugin"]


@pytest.mark.usefixtures("setup_env_variables")
def test_init_of_sdk():
    armis_sdk = ArmisSdk()

    assert isinstance(armis_sdk.client, ArmisClient)
    assert isinstance(armis_sdk.data_export, DataExportClient)
    assert isinstance(armis_sdk.sites, SitesClient)
