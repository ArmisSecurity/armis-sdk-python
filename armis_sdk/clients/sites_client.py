from typing import AsyncIterator
from typing import List

import universalasync

from armis_sdk.clients.network_equipment_client import NetworkEquipmentClient
from armis_sdk.clients.site_integrations_client import SiteIntegrationsClient
from armis_sdk.core import response_utils
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.core.base_entity_client import BaseEntityClient
from armis_sdk.entities.site import Site


@universalasync.wrap
class SitesClient(BaseEntityClient):
    # pylint: disable=line-too-long
    """
    A client for interacting with sites.

    The primary entity for this client is [Site][armis_sdk.entities.site.Site].

    Attributes:
        network_equipment_client (NetworkEquipmentClient): An instance of [NetworkEquipmentClient][armis_sdk.clients.network_equipment_client.NetworkEquipmentClient]
        site_integrations_client (SiteIntegrationsClient): An instance of [SiteIntegrationsClient][armis_sdk.clients.site_integrations_client.SiteIntegrationsClient]
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.network_equipment_client = NetworkEquipmentClient(self._armis_client)
        self.site_integrations_client = SiteIntegrationsClient(self._armis_client)

    async def create(self, site: Site) -> Site:
        """Create a `Site`.

        Args:
            site: The site to delete.

        Returns:
            The same site as the input with the addition of id.

        Example:
            Example:
            ```python linenums="1" hl_lines="10"
            import asyncio

            from armis_sdk.clients.sites_client import SitesClient
            from armis_sdk.entities.site import Site


            async def main():
                sites_client = SitesClient()
                site_to_create = Site(name="my site")
                print(await sites_client.create(site_to_create))

            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Site(id=1, name="my site")
            ```
        """
        if site.id is not None:
            raise ArmisError(
                "Can't create a site that already has an id. "
                "Did you mean to call `.update(site)`?"
            )

        if not site.name:
            raise ArmisError("Can't create a site without a name.")

        payload = site.model_dump(
            by_alias=True,
            exclude={"children", "network_equipment_device_ids"},
            exclude_none=True,
        )
        async with self._armis_client.client() as client:
            response = await client.post("/api/v1/sites/", json=payload)
            data = response_utils.get_data_dict(response)
            created_site = site.model_copy(update={"id": int(data["id"])}, deep=True)

        if site.network_equipment_device_ids:
            await self.network_equipment_client.add(
                created_site, site.network_equipment_device_ids
            )

        return created_site

    async def delete(self, site: Site):
        """Delete a `Site`.

        Args:
            site: The site to delete.

        Example:
            Example:
            ```python linenums="1" hl_lines="10"
            import asyncio

            from armis_sdk.clients.sites_client import SitesClient
            from armis_sdk.entities.site import Site


            async def main():
                sites_client = SitesClient()
                site = Site(id=1)
                await sites_client.delete(site)

            asyncio.run(main())
            ```
        """
        if site.id is None:
            raise ArmisError("Can't delete a site without an id.")

        async with self._armis_client.client() as client:
            response = await client.delete(f"/api/v1/sites/{site.id}/")
            response_utils.raise_for_status(response)

    async def get(self, site_id: str) -> Site:
        """Get a `Site` by its ID.

        Args:
            site_id: The ID of the site to get.

        Returns:
            A `Site` object.

        Example:
            Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.sites_client import SitesClient


            async def main():
                sites_client = SitesClient()
                print(await sites_client.get("1"))

            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Site(id=1)
            ```
        """
        async with self._armis_client.client() as client:
            response = await client.get(f"/api/v1/sites/{site_id}/")
            data = response_utils.get_data_dict(response)
            return Site.model_validate(data)

    async def hierarchy(self) -> List[Site]:
        """Create a hierarchy of the tenant's sites, taking into account the parent-child relationships.

        Returns:
            A list of `Site` objects, that are themselves not children of any other site.
            Each site has a `.children` property that includes its direct children.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.sites_client import SitesClient


            async def main():
                sites_client = SitesClient()
                print(await sites_client.hierarchy())

            asyncio.run(main())
            ```
            Will output this structure (depending on the actual data):
            ```python linenums="1"
            [
                Site(
                    id=1,
                    children=[
                        Site(id=3),
                    ],
                ),
                Site(id=2),
            ]
            ```
        """
        id_to_site = {site.id: site async for site in self.list()}
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


            async def main():
                sites_client = SitesClient()
                async for site in sites_client.list()
                    print(site)

            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Site(id=1)
            Site(id=2)
            ```
        """
        async for item in self._list("/api/v1/sites/", "sites", Site):
            yield item

    async def update(self, site: Site):
        """Update a site's properties.

        Args:
            site: The site to update.

        Raises:
            ResponseError: If an error occurs while communicating with the API.

        Example:
            ```python linenums="1" hl_lines="10"
            import asyncio

            from armis_sdk.clients.sites_client import SitesClient
            from armis_sdk.entities.site import Site


            async def main():
                sites_client = SitesClient()
                site = Site(id=1, location="new location")
                await sites_client.update(site)

            asyncio.run(main())
            ```
        """
        if site.id is None:
            raise ArmisError(
                "Can't update a site without an id. "
                "Did you mean to call `.create(site)`?"
            )

        data = site.model_dump(
            by_alias=True,
            exclude={
                "children",
                "id",
                "integration_ids",
                "network_equipment_device_ids",
            },
            exclude_none=True,
        )

        if data:
            async with self._armis_client.client() as client:
                response = await client.patch(f"/api/v1/sites/{site.id}/", json=data)
                response_utils.raise_for_status(response)

        if site.network_equipment_device_ids is not None:
            await self.network_equipment_client.update(site)

        if site.integration_ids is not None:
            await self.site_integrations_client.update(site)
