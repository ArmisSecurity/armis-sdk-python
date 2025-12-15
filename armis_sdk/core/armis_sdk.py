from typing import Optional

from armis_sdk.clients.assets_client import AssetsClient
from armis_sdk.clients.collectors_client import CollectorsClient
from armis_sdk.clients.data_export_client import DataExportClient
from armis_sdk.clients.device_custom_properties_client import (
    DeviceCustomPropertiesClient,
)
from armis_sdk.clients.sites_client import SitesClient
from armis_sdk.core.armis_client import ArmisClient
from armis_sdk.core.client_credentials import ClientCredentials


class ArmisSdk:  # pylint: disable=too-few-public-methods
    # pylint: disable=line-too-long
    """
    The `ArmisSdk` class provides access to the Armis API, while conveniently wraps
    common actions like authentication, pagination, parsing etc.

    Attributes:
        client (ArmisClient): An instance of [ArmisClient][armis_sdk.core.armis_client.ArmisClient]
        assets (AssetsClient): An instance of [AssetsClient][armis_sdk.clients.assets_client.AssetsClient]
        collectors (CollectorsClient): An instance of [CollectorsClient][armis_sdk.clients.collectors_client.CollectorsClient]
        data_export (DataExportClient): An instance of [DataExportClient][armis_sdk.clients.data_export_client.DataExportClient]
        device_custom_properties (DeviceCustomPropertiesClient): An instance of [DeviceCustomPropertiesClient][armis_sdk.clients.device_custom_properties_client.DeviceCustomPropertiesClient]
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

    def __init__(self, credentials: Optional[ClientCredentials] = None):
        self.client: ArmisClient = ArmisClient(credentials=credentials)
        self.assets: AssetsClient = AssetsClient(self.client)
        self.collectors: CollectorsClient = CollectorsClient(self.client)
        self.data_export: DataExportClient = DataExportClient(self.client)
        self.device_custom_properties: DeviceCustomPropertiesClient = (
            DeviceCustomPropertiesClient(self.client)
        )
        self.sites: SitesClient = SitesClient(self.client)
