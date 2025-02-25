from typing import Optional

from armis_sdk.clients.sites_client import SitesClient
from armis_sdk.core.armis_client import ArmisClient

ARMIS_SECRET_KEY = "ARMIS_SECRET_KEY"
ARMIS_TENANT = "ARMIS_TENANT"
ARMIS_CLIENT_ID = "ARMIS_CLIENT_ID"


class ArmisSdk:  # pylint: disable=too-few-public-methods
    # pylint: disable=line-too-long
    """
    The `ArmisSdk` class provides access to the Armis API, while conveniently wraps
    common actions like authentication, pagination, parsing etc.

    Attributes:
        client (ArmisClient): An instance of [ArmisClient][armis_sdk.core.armis_client.ArmisClient]
        sites (SitesClient): An instance of [SitesClient][armis_sdk.clients.sites_client.SitesClient]

    Example:
        ```python linenums="1" hl_lines="3"
        import asyncio

        from armis_sdk import ArmisSdk

        armis_sdk = ArmisSdk()

        async def main():
            async for site in await armis_sdk.sites.list():
                print(site)

        asyncio.run(main())
        ```
    """

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
