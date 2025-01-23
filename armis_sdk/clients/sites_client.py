from typing import AsyncIterator
from typing import List

from httpx import HTTPStatusError

from armis_sdk.clients.network_equipment_client import NetworkEquipmentClient
from armis_sdk.core.armis_error import ResponseError
from armis_sdk.core.base_entity_client import BaseEntityClient
from armis_sdk.entities.site import Site


class SitesClient(BaseEntityClient):
    # pylint: disable=line-too-long
    """
    A client for interacting with sites.

    The primary entity for this client is [Site][armis_sdk.entities.site.Site].

    Attributes:
        network_equipment_client (NetworkEquipmentClient): An instance of [NetworkEquipmentClient][armis_sdk.clients.network_equipment_client.NetworkEquipmentClient]
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.network_equipment_client = NetworkEquipmentClient(self._armis_client)

    async def hierarchy(self) -> List[Site]:
        """Create a hierarchy of the tenant's sites, taking into account the parent-child relationships.

        Returns:
            A list of `Site` objects, that are themselves not children of any other site.
            Each site has a `.children` property that includes its direct children.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.sites_client import SitesClient

            sites_client = SitesClient()

            async def main():
                print(await sites_client.hierarchy())

            asyncio.run(main())
            ```
            Will output this structure (depending on the actual data):
            ```python linenums="1"
            [
                Site(
                    id="1",
                    children=[
                        Site(id="3"),
                    ],
                ),
                Site(id="2"),
            ]
            ```
        """
        id_to_site = {site.id: site async for site in await self.list()}
        root = []
        for site in id_to_site.values():
            if parent := id_to_site.get(site.parent_id):
                parent.children.append(site)
            else:
                root.append(site)

        return root

    async def list(self) -> AsyncIterator[Site]:
        """List all the tenant's sites.
        This method takes care of pagination, so you don't have to deal with it.

        Returns:
            An (async) iterator of `Site` object.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.sites_client import SitesClient

            sites_client = SitesClient()

            async def main():
                async for site in await sites_client.list()
                    print(site)

            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Site(id="1")
            Site(id="2")
            ```
        """
        return self._paginate("/api/v1/sites/", "sites", Site)

    async def update(self, site: Site):
        """Update a site's properties.

        Args:
            site: The site to update.

        Raises:
            ResponseError: If an error occurs while communicating with the API.

        Example:
            ```python linenums="1" hl_lines="9"
            import asyncio

            from armis_sdk.clients.sites_client import SitesClient

            sites_client = SitesClient()

            async def main():
                site = Site(id="1", location="new location")
                await sites_client.update(site)

            asyncio.run(main())
            ```
        """
        data = site.model_dump(
            exclude={"children", "id", "network_equipment_device_ids"},
            exclude_none=True,
        )

        if data:
            async with self._armis_client.client() as client:
                response = await client.patch(f"/api/v1/sites/{site.id}/", json=data)
                try:
                    response.raise_for_status()
                except HTTPStatusError as error:
                    raise ResponseError(
                        f"Error while updating site with id {site.id!r} ",
                        response_errors=[error],
                    ) from error

        if site.network_equipment_device_ids is not None:
            await self.network_equipment_client.update(site)
