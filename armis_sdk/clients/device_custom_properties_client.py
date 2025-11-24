from typing import AsyncIterator

import universalasync

from armis_sdk.core import response_utils
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.core.base_entity_client import BaseEntityClient
from armis_sdk.entities.device_custom_property import DeviceCustomProperty


@universalasync.wrap
class DeviceCustomPropertiesClient(BaseEntityClient):
    """
    A client for interacting with device custom properties.

    The primary entity for this client is
    [DeviceCustomProperty][armis_sdk.entities.device_custom_property.DeviceCustomProperty].
    """

    async def create(self, property_: DeviceCustomProperty) -> DeviceCustomProperty:
        # pylint: disable=line-too-long
        """Create a `DeviceCustomProperty`.

        Args:
            property_: The `DeviceCustomProperty` to create.

        Returns:
            The same property as the input with the addition of id.

        Example:
            Example:
            ```python linenums="1" hl_lines="10"
            import asyncio

            from armis_sdk.clients.device_custom_properties_client import DeviceCustomPropertiesClient
            from armis_sdk.entities.device_custom_property import DeviceCustomProperty


            async def main():
                client = DeviceCustomPropertiesClient()
                property_ = DeviceCustomProperty(name="MyConfig", type="string")
                print(await client.create(property_))

            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            DeviceCustomPropertiesClient(id=1, name="MyConfig", type="string")
            ```
        """
        if property_.id is not None:
            raise ArmisError(
                "Can't create a property that already has an id. "
                "Did you mean to call `.update(property_)`?",
            )

        if not property_.name:
            raise ArmisError("Can't create a property without a name.")

        if not property_.type:
            raise ArmisError("Can't create a property without a type.")

        payload = property_.model_dump(exclude_none=True)

        async with self._armis_client.client() as client:
            response = await client.post(
                "/v3/settings/device-custom-properties", json=payload
            )
            data = response_utils.get_data_dict(response)
            return DeviceCustomProperty.model_validate(data)

    async def delete(self, property_: DeviceCustomProperty):
        # pylint: disable=line-too-long
        """Delete a `DeviceCustomProperty`.

        Args:
            property_: The `DeviceCustomProperty` to delete.

        Example:
            Example:
            ```python linenums="1" hl_lines="10"
            import asyncio

            from armis_sdk.clients.device_custom_properties_client import DeviceCustomPropertiesClient
            from armis_sdk.entities.device_custom_property import DeviceCustomProperty


            async def main():
                client = DeviceCustomPropertiesClient()
                property_ = DeviceCustomProperty(id=1, name="MyConfig", type="string")
                await client.delete(property_)

            asyncio.run(main())
            ```
        """
        if property_.id is None:
            raise ArmisError("Can't delete a property without an id.")

        async with self._armis_client.client() as client:
            response = await client.delete(
                f"/v3/settings/device-custom-properties/{property_.id}"
            )
            response_utils.raise_for_status(response)

    async def get(self, property_id: int) -> DeviceCustomProperty:
        # pylint: disable=line-too-long
        """Get a `DeviceCustomProperty` by its ID.

        Args:
            property_id: The ID of the `DeviceCustomProperty` to get.

        Returns:
            A `DeviceCustomProperty` object.

        Example:
            Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.device_custom_properties_client import DeviceCustomPropertiesClient


            async def main():
                client = DeviceCustomPropertiesClient()
                print(await client.get(1))

            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            DeviceCustomPropertiesClient(id=1, name="MyConfig", type="string")
            ```
        """
        async with self._armis_client.client() as client:
            response = await client.get(
                f"/v3/settings/device-custom-properties/{property_id}"
            )
            data = response_utils.get_data_dict(response)
            return DeviceCustomProperty.model_validate(data)

    async def list(self) -> AsyncIterator[DeviceCustomProperty]:
        # pylint: disable=line-too-long
        """List all the tenant's `DeviceCustomProperty`s.
        This method takes care of pagination, so you don't have to deal with it.

        Returns:
            An (async) iterator of `DeviceCustomProperty` object.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.device_custom_properties_client import DeviceCustomPropertiesClient


            async def main():
                client = DeviceCustomPropertiesClient()
                async for property_ in client.list()
                    print(property_)

            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            DeviceCustomPropertiesClient(id=1, name="MyConfig", type="string")
            DeviceCustomPropertiesClient(id=1, name="MyOtherConfig", type="integer")
            ```
        """

        async with self._armis_client.client() as client:
            # endpoint doesn't support paging
            response = await client.get("/v3/settings/device-custom-properties")
            data = response_utils.get_data_dict(response)
            for item in data["items"]:
                yield DeviceCustomProperty.model_validate(item)

    async def update(self, property_: DeviceCustomProperty) -> DeviceCustomProperty:
        # pylint: disable=line-too-long
        """Update a `DeviceCustomProperty`.
        Only `description` and `allowed_values` are updatable.

        Args:
            property_: The `DeviceCustomProperty` to update.

        Raises:
            ResponseError: If an error occurs while communicating with the API.

        Example:
            ```python linenums="1" hl_lines="15"
            import asyncio

            from armis_sdk.clients.device_custom_properties_client import DeviceCustomPropertiesClient
            from armis_sdk.entities.device_custom_property import DeviceCustomProperty


            async def main():
                client = DeviceCustomPropertiesClient()
                property_ = DeviceCustomProperty(
                    id=1,
                    name="MyConfig",
                    type="string",
                    description="New description",
                )
                await client.update(property_)

            asyncio.run(main())
            ```
        """
        if property_.id is None:
            raise ArmisError(
                "Can't update a property without an id. "
                "Did you mean to call `.create(property_)`?",
            )

        data = property_.model_dump(
            exclude={"id", "name", "creation_time", "created_by", "type"},
            exclude_none=True,
        )

        if not data:
            return property_

        async with self._armis_client.client() as client:
            response = await client.patch(
                f"/v3/settings/device-custom-properties/{property_.id}",
                json=data,
            )
            response_utils.raise_for_status(response)

        return property_
