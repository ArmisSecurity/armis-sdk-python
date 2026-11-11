import universalasync

from armis_sdk.core import response_utils
from armis_sdk.core.base_entity_client import BaseEntityClient
from armis_sdk.entities.alert import Alert


@universalasync.wrap
class AlertsClient(BaseEntityClient):
    """
    A client for interacting with alerts.

    The primary entity for this client is [Alert][armis_sdk.entities.alert.Alert].
    """

    async def get(self, alert_id: int) -> Alert:
        """Get an `Alert` by its ID.

        Args:
            alert_id: The ID of the alert to get.

        Returns:
            An `Alert` object.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.alerts_client import AlertsClient


            async def main():
                alerts_client = AlertsClient()
                print(await alerts_client.get(42))


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Alert(id=42, severity="HIGH", ...)
            ```
        """
        async with self._armis_client.client() as client:
            response = await client.get(f"/v3/alerts/{alert_id}")
            data = response_utils.get_data_dict(response)
            return Alert.model_validate(data)
