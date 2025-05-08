from typing import Optional

from armis_sdk.clients.sites_client import SitesClient
from armis_sdk.core import armis_client
from armis_sdk.core.armis_client import ArmisClient


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
            async for site in armis_sdk.sites.list():
                print(site)

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        tenant: Optional[str] = None,
        secret_key: Optional[str] = None,
        client_id: Optional[str] = None,
        base_domain: Optional[str] = armis_client.BASE_DOMAIN,
    ):
        self.client = ArmisClient(
            tenant=tenant,
            client_id=client_id,
            secret_key=secret_key,
            base_domain=base_domain,
        )
        self.sites = SitesClient(self.client)
