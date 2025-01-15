from typing import Optional

from armis_sdk.core.armis_client import ArmisClient
from armis_sdk.sdks.site_sdk import SitesSdk

ARMIS_SECRET_KEY = "ARMIS_SECRET_KEY"
ARMIS_TENANT = "ARMIS_TENANT"
ARMIS_CLIENT_ID = "ARMIS_CLIENT_ID"


class ArmisSdk:  # pylint: disable=too-few-public-methods
    def __init__(
        self,
        tenant: Optional[str] = None,
        secret_key: Optional[str] = None,
        client_id: Optional[str] = None,
    ):
        self.client = ArmisClient(
            tenant=tenant, client_id=client_id, secret_key=secret_key
        )
        self.sites = SitesSdk(self.client)
