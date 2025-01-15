from typing import Optional

from armis_sdk.clients.sites_client import SitesClient
from armis_sdk.core.armis_client import ArmisClient

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
        self.sites = SitesClient(self.client)
