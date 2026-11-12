from armis_sdk.clients.alerts_client import AlertsClient
from armis_sdk.clients.arps_client import ArpsClient
from armis_sdk.clients.assets_client import AssetsClient
from armis_sdk.clients.boundaries_client import BoundariesClient
from armis_sdk.clients.collectors_client import CollectorsClient
from armis_sdk.clients.data_export_client import DataExportClient
from armis_sdk.clients.device_custom_properties_client import DeviceCustomPropertiesClient
from armis_sdk.clients.integrations_client import IntegrationsClient
from armis_sdk.clients.policies_client import PoliciesClient
from armis_sdk.clients.sites_client import SitesClient
from armis_sdk.core.armis_client import ArmisClient
from armis_sdk.core.client_credentials import ClientCredentials


class ArmisSdk:
    """
    The `ArmisSdk` class provides access to the Armis API, while conveniently wraps
    common actions like authentication, pagination, parsing etc.

    Attributes:
        client (ArmisClient): An instance of [ArmisClient][armis_sdk.core.armis_client.ArmisClient]
        alerts (AlertsClient): An instance of [AlertsClient][armis_sdk.clients.alerts_client.AlertsClient]
        arps (ArpsClient): An instance of [ArpsClient][armis_sdk.clients.arps_client.ArpsClient]
        assets (AssetsClient): An instance of [AssetsClient][armis_sdk.clients.assets_client.AssetsClient]
        boundaries (BoundariesClient): An instance of [BoundariesClient][armis_sdk.clients.boundaries_client.BoundariesClient]
        collectors (CollectorsClient): An instance of [CollectorsClient][armis_sdk.clients.collectors_client.CollectorsClient]
        data_export (DataExportClient): An instance of [DataExportClient][armis_sdk.clients.data_export_client.DataExportClient]
        device_custom_properties (DeviceCustomPropertiesClient): An instance of [DeviceCustomPropertiesClient][armis_sdk.clients.device_custom_properties_client.DeviceCustomPropertiesClient]
        integrations (IntegrationsClient): An instance of [IntegrationsClient][armis_sdk.clients.integrations_client.IntegrationsClient]
        policies (PoliciesClient): An instance of [PoliciesClient][armis_sdk.clients.policies_client.PoliciesClient]
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

    def __init__(self, credentials: ClientCredentials | None = None):
        self.client: ArmisClient = ArmisClient(credentials=credentials)
        self.alerts: AlertsClient = AlertsClient(self.client)
        self.arps: ArpsClient = ArpsClient(self.client)
        self.assets: AssetsClient = AssetsClient(self.client)
        self.boundaries: BoundariesClient = BoundariesClient(self.client)
        self.collectors: CollectorsClient = CollectorsClient(self.client)
        self.data_export: DataExportClient = DataExportClient(self.client)
        self.device_custom_properties: DeviceCustomPropertiesClient = DeviceCustomPropertiesClient(self.client)
        self.integrations: IntegrationsClient = IntegrationsClient(self.client)
        self.policies: PoliciesClient = PoliciesClient(self.client)
        self.sites: SitesClient = SitesClient(self.client)
