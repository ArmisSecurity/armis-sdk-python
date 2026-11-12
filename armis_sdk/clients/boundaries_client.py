from collections.abc import AsyncIterator

import universalasync

from armis_sdk.core import response_utils
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.core.base_entity_client import BaseEntityClient
from armis_sdk.entities.boundary import Boundary


@universalasync.wrap
class BoundariesClient(BaseEntityClient):
    """
    A client for interacting with boundaries.

    The primary entity for this client is [Boundary][armis_sdk.entities.boundary.Boundary].
    """

    async def create(self, boundary: Boundary) -> Boundary:
        """Create a `Boundary`.

        Args:
            boundary: The boundary to create.

        Returns:
            The created boundary, including its id.

        Example:
            ```python linenums="1" hl_lines="11"
            import asyncio

            from armis_sdk.clients.boundaries_client import BoundariesClient
            from armis_sdk.entities.asq_rule import AsqRule
            from armis_sdk.entities.boundary import Boundary


            async def main():
                boundaries_client = BoundariesClient()
                boundary = Boundary(name="Corporate", asq_rule=AsqRule.from_asq("in:devices ipAddress:10.0.0.0/8"))
                print(await boundaries_client.create(boundary))


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Boundary(id=1, name="Corporate", ...)
            ```
        """
        if boundary.id is not None:
            raise ArmisError(
                "Can't create a boundary that already has an id. Did you mean to call `.update(boundary)`?"
            )

        if not boundary.name:
            raise ArmisError("Can't create a boundary without a name.")

        payload = boundary.model_dump(exclude={"id", "sites"}, exclude_none=True)
        async with self._armis_client.client() as client:
            response = await client.post("/v3/settings/boundaries", json=payload)
            data = response_utils.get_data_dict(response)
            return Boundary.model_validate(data)

    async def delete(self, boundary: Boundary):
        """Delete a `Boundary`.

        Args:
            boundary: The boundary to delete.

        Example:
            ```python linenums="1" hl_lines="10"
            import asyncio

            from armis_sdk.clients.boundaries_client import BoundariesClient
            from armis_sdk.entities.boundary import Boundary


            async def main():
                boundaries_client = BoundariesClient()
                boundary = Boundary(id=1)
                await boundaries_client.delete(boundary)


            asyncio.run(main())
            ```
        """
        if boundary.id is None:
            raise ArmisError("Can't delete a boundary without an id.")

        async with self._armis_client.client() as client:
            response = await client.delete(f"/v3/settings/boundaries/{boundary.id}")
            response_utils.raise_for_status(response)

    async def get(self, boundary_id: int) -> Boundary:
        """Get a `Boundary` by its ID.

        Args:
            boundary_id: The ID of the boundary to get.

        Returns:
            A `Boundary` object.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.boundaries_client import BoundariesClient


            async def main():
                boundaries_client = BoundariesClient()
                print(await boundaries_client.get(1))


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Boundary(id=1, name="Corporate", ...)
            ```
        """
        async with self._armis_client.client() as client:
            response = await client.get(f"/v3/settings/boundaries/{boundary_id}")
            data = response_utils.get_data_dict(response)
            return Boundary.model_validate(data)

    async def list(self) -> AsyncIterator[Boundary]:
        """List all the tenant's boundaries.
        This method takes care of pagination, so you don't have to deal with it.

        Returns:
            An (async) iterator of `Boundary` object.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.boundaries_client import BoundariesClient


            async def main():
                boundaries_client = BoundariesClient()
                async for boundary in boundaries_client.list():
                    print(boundary)


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Boundary(id=1, name="Corporate", ...)
            Boundary(id=2, name="Guests", ...)
            ```
        """
        async for item in self._list("/v3/settings/boundaries", Boundary):
            yield item

    async def update(self, boundary: Boundary) -> Boundary:
        """Update a boundary's properties.
        Only the `name`, `asq_rule` and `site_ids` fields are updatable.

        Args:
            boundary: The boundary to update.

        Returns:
            The updated boundary.

        Raises:
            ResponseError: If an error occurs while communicating with the API.

        Example:
            ```python linenums="1" hl_lines="10"
            import asyncio

            from armis_sdk.clients.boundaries_client import BoundariesClient
            from armis_sdk.entities.boundary import Boundary


            async def main():
                boundaries_client = BoundariesClient()
                boundary = Boundary(id=1, name="New name")
                await boundaries_client.update(boundary)


            asyncio.run(main())
            ```
        """
        if boundary.id is None:
            raise ArmisError("Can't update a boundary without an id. Did you mean to call `.create(boundary)`?")

        data = boundary.model_dump(exclude={"id", "sites"}, exclude_none=True)

        if not data:
            return boundary

        async with self._armis_client.client() as client:
            response = await client.patch(f"/v3/settings/boundaries/{boundary.id}", json=data)
            data = response_utils.get_data_dict(response)
            return Boundary.model_validate(data)
