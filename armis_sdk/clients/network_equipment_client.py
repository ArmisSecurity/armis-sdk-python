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
class NetworkEquipmentClient(
    BaseEntityClient
):  # pylint: disable=too-few-public-methods
    """
    A client for interacting with a site's network equipment.

    The primary entity for this client is [Site][armis_sdk.entities.site.Site].
    """

    async def add(self, site: Site, network_equipment_device_ids: List[int]):
        """Add network equipment devices to a site.

        Args:
            site: The site to update.
            network_equipment_device_ids: The network equipment device IDs to add.

        Example:
            ```python linenums="1" hl_lines="9"
            import asyncio

            from armis_sdk.clients.network_equipment_client import NetworkEquipmentClient


            async def main():
                network_equipment_client = NetworkEquipmentClient()
                site = Site(id=1)
                await network_equipment_client.add(site, [1, 2, 3])

            asyncio.run(main())
            ```
        """
        if site.id is None:
            raise ArmisError("The property 'id' must be set.")

        if not network_equipment_device_ids:
            return

        await self._insert(site.id, set(network_equipment_device_ids))

    async def update(self, site: Site):
        """Update a site's network equipment devices.

        Args:
            site: The site to update.

        Raises:
            ResponseError: If an error occurs while communicating with the API.
            ArmisError: If `site.network_equipment_device_ids` is not set.

        Example:
            ```python linenums="1" hl_lines="9"
            import asyncio

            from armis_sdk.clients.network_equipment_client import NetworkEquipmentClient


            async def main():
                network_equipment_client = NetworkEquipmentClient()
                site = Site(id=1, network_equipment_device_ids=[1, 2, 3])
                await network_equipment_client.update(site)

            asyncio.run(main())
            ```
        """

        if site.id is None:
            raise ArmisError("The property 'id' must be set.")

        if site.network_equipment_device_ids is None:
            raise ArmisError("The property 'network_equipment_device_ids' must be set.")

        new_ids = set(site.network_equipment_device_ids)
        current_ids = set(await self._list_ids(site.id))

        await self._insert(site.id, new_ids - current_ids)
        await self._delete(site.id, current_ids - new_ids)

    async def _delete(self, site_id: int, network_equipment_device_ids: Set[int]):
        if not network_equipment_device_ids:
            return

        errors = []
        async with self._armis_client.client() as client:
            for device_id in network_equipment_device_ids:
                response = await client.delete(
                    f"/api/v1/sites/{site_id}/network-equipment/{device_id}/"
                )
                try:
                    response.raise_for_status()
                except HTTPStatusError as error:
                    errors.append(error)

        if errors:
            raise ResponseError(
                "Error while deleting network equipment "
                f"device ids {network_equipment_device_ids!r} from site {site_id!r} ",
                response_errors=errors,
            )

    async def _insert(self, site_id: int, network_equipment_device_ids: Set[int]):
        if not network_equipment_device_ids:
            return

        async with self._armis_client.client() as client:
            response = await client.post(
                f"/api/v1/sites/{site_id}/network-equipment/_bulk/",
                json={"networkEquipmentDeviceIds": list(network_equipment_device_ids)},
            )
            response_utils.raise_for_status(response)

    async def _list_ids(self, site_id) -> List[int]:
        async with self._armis_client.client() as client:
            response = await client.get(f"/api/v1/sites/{site_id}/network-equipment/")
            data = response_utils.get_data_dict(response)
        return data["networkEquipmentDeviceIds"]
