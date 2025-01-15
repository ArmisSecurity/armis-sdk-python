import pytest

from armis_sdk import ArmisSdk
from armis_sdk.core.armis_client import ArmisClient
from armis_sdk.sdks.site_sdk import SitesSdk

pytest_plugins = ["tests.plugins.setup_plugin"]


@pytest.mark.usefixtures("setup_env_variables")
def test_init_of_sdk():
    armis_sdk = ArmisSdk()

    assert isinstance(armis_sdk.client, ArmisClient)
    assert isinstance(armis_sdk.sites, SitesSdk)
