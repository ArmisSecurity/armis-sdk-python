from typing import List
from typing import Set

import universalasync
from httpx import HTTPStatusError

from armis_sdk.core import response_utils
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.core.armis_error import ResponseError
from armis_sdk.core.base_entity_client import BaseEntityClient
from armis_sdk.entities.site import Site


@universalasync.wrap
class SiteIntegrationsClient(
    BaseEntityClient
):  # pylint: disable=too-few-public-methods
    """
    A client for interacting with a site's integrations.

    The primary entity for this client is [Site][armis_sdk.entities.site.Site].
    """

    async def update(self, site: Site):
        """Update a site's integrations.

        Args:
            site: The site to update.

        Raises:
            ResponseError: If an error occurs while communicating with the API.
            ArmisError: If `site.integration_ids` is not set.

        Example:
            ```python linenums="1" hl_lines="9"
            import asyncio

            from armis_sdk.clients.site_integrations_client import SiteIntegrationsClient


            async def main():
                site_integrations_client = SiteIntegrationsClient()
                site = Site(id=1, integration_ids=[1, 2, 3])
                await site_integrations_client.update(site)

            asyncio.run(main())
            ```
        """

        if site.id is None:
            raise ArmisError("The property 'id' must be set.")

        if site.integration_ids is None:
            raise ArmisError("The property 'integration_ids' must be set.")

        new_ids = set(site.integration_ids)
        current_ids = set(await self._list_ids(site.id))

        await self._insert(site.id, new_ids - current_ids)
        await self._delete(site.id, current_ids - new_ids)

    async def _delete(self, site_id: int, integration_ids: Set[int]):
        if not integration_ids:
            return

        errors = []
        async with self._armis_client.client() as client:
            for integration_id in integration_ids:
                response = await client.delete(
                    f"/api/v1/sites/{site_id}/integrations-ids/{integration_id}/"
                )
                try:
                    response.raise_for_status()
                except HTTPStatusError as error:
                    errors.append(error)

        if errors:
            raise ResponseError(
                "Error while deleting integration ids "
                f"{integration_ids!r} from site {site_id!r} ",
                response_errors=errors,
            )

    async def _insert(self, site_id: int, integration_ids: Set[int]):
        if not integration_ids:
            return

        errors = []
        async with self._armis_client.client() as client:
            for integration_id in integration_ids:
                response = await client.post(
                    f"/api/v1/sites/{site_id}/integrations-ids/",
                    json={"integrationId": integration_id},
                )
                try:
                    response.raise_for_status()
                except HTTPStatusError as error:
                    errors.append(error)

        if errors:
            raise ResponseError(
                "Error while inserting integration ids "
                f"{integration_ids!r} to site {site_id!r} ",
                response_errors=errors,
            )

    async def _list_ids(self, site_id: int) -> List[int]:
        async with self._armis_client.client() as client:
            response = await client.get(f"/api/v1/sites/{site_id}/integrations-ids/")
            data = response_utils.get_data_dict(response)
        return data["integrationIds"]
