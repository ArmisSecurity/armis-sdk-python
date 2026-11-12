import builtins
from collections.abc import AsyncIterator
from typing import Literal

import universalasync

from armis_sdk.core import response_utils
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.core.base_entity_client import BaseEntityClient
from armis_sdk.entities.integration import Integration


_READ_ONLY_FIELDS = {"id", "creation_time", "params_change_time", "current_state", "statistics"}


@universalasync.wrap
class IntegrationsClient(BaseEntityClient):
    """
    A client for interacting with integrations.

    The primary entity for this client is [Integration][armis_sdk.entities.integration.Integration].
    """

    async def create(self, integration: Integration) -> Integration:
        """Create an `Integration`.

        Args:
            integration: The integration to create.

        Returns:
            The created integration, including its ID.

        Example:
            ```python linenums="1" hl_lines="14"
            import asyncio

            from armis_sdk.clients.integrations_client import IntegrationsClient
            from armis_sdk.entities.integration import Integration


            async def main():
                integrations_client = IntegrationsClient()
                integration = Integration(
                    name="CrowdStrike",
                    instance_name="My CrowdStrike",
                    params={"client_id": "..."},
                )
                print(await integrations_client.create(integration))


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Integration(id=1, name="CrowdStrike", instance_name="My CrowdStrike", ...)
            ```
        """
        if integration.id is not None:
            raise ArmisError(
                "Can't create an integration that already has an id. Did you mean to call `.update(integration)`?"
            )

        if not integration.name:
            raise ArmisError("Can't create an integration without a name.")

        if not integration.instance_name:
            raise ArmisError("Can't create an integration without an instance name.")

        if integration.params is None:
            raise ArmisError("Can't create an integration without params.")

        payload = integration.model_dump(exclude=_READ_ONLY_FIELDS, exclude_none=True)
        async with self._armis_client.client() as client:
            response = await client.post("/v3/settings/integrations", json=payload)
            data = response_utils.get_data_dict(response)
            return Integration.model_validate(data)

    async def delete(self, integration: Integration):
        """Delete an `Integration`.

        Args:
            integration: The integration to delete.

        Example:
            ```python linenums="1" hl_lines="10"
            import asyncio

            from armis_sdk.clients.integrations_client import IntegrationsClient
            from armis_sdk.entities.integration import Integration


            async def main():
                integrations_client = IntegrationsClient()
                integration = Integration(id=1)
                await integrations_client.delete(integration)


            asyncio.run(main())
            ```
        """
        if integration.id is None:
            raise ArmisError("Can't delete an integration without an id.")

        async with self._armis_client.client() as client:
            response = await client.delete(f"/v3/settings/integrations/{integration.id}")
            response_utils.raise_for_status(response)

    async def get(self, integration_id: int) -> Integration:
        """Get an `Integration` by its ID.

        Args:
            integration_id: The ID of the integration to get.

        Returns:
            An `Integration` object.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.integrations_client import IntegrationsClient


            async def main():
                integrations_client = IntegrationsClient()
                print(await integrations_client.get(1))


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Integration(id=1, name="CrowdStrike", ...)
            ```
        """
        async with self._armis_client.client() as client:
            response = await client.get(f"/v3/settings/integrations/{integration_id}")
            data = response_utils.get_data_dict(response)
            return Integration.model_validate(data)

    async def list(self) -> AsyncIterator[Integration]:
        """List all the tenant's integrations.
        This method takes care of pagination, so you don't have to deal with it.

        Returns:
            An (async) iterator of `Integration` objects.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.integrations_client import IntegrationsClient


            async def main():
                integrations_client = IntegrationsClient()
                async for integration in integrations_client.list():
                    print(integration)


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Integration(id=1, name="CrowdStrike", ...)
            Integration(id=2, name="Active Directory", ...)
            ```
        """
        async for item in self._list("/v3/settings/integrations", Integration):
            yield item

    async def search(
        self,
        ids: builtins.list[int] | None = None,
        names: builtins.list[str] | None = None,
        states: builtins.list[Literal["ACTIVE", "DRAFT", "INACTIVE"]] | None = None,
        collector_ids: builtins.list[int] | None = None,
        broker_ids: builtins.list[int] | None = None,
    ) -> AsyncIterator[Integration]:
        """Search integrations that match all of the given criteria.
        This method takes care of pagination, so you don't have to deal with it.

        Args:
            ids: Only include integrations with these IDs.
            names: Only include integrations with these display names (e.g. `"CrowdStrike"`).
            states: Only include integrations in these states.
            collector_ids: Only include integrations associated with these collector IDs.
            broker_ids: Only include integrations associated with these broker IDs.

        Returns:
            An (async) iterator of `Integration` objects.

        Raises:
            ArmisError: If no criteria were given.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.integrations_client import IntegrationsClient


            async def main():
                integrations_client = IntegrationsClient()
                async for integration in integrations_client.search(names=["CrowdStrike"], states=["ACTIVE"]):
                    print(integration)


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Integration(id=1, name="CrowdStrike", state="ACTIVE", ...)
            ```
        """
        filter_ = {
            key: value
            for key, value in {
                "ids": ids,
                "names": names,
                "states": states,
                "collector_ids": collector_ids,
                "broker_ids": broker_ids,
            }.items()
            if value is not None
        }
        if not filter_:
            raise ArmisError("At least one search criterion is required.")

        async for item in self._armis_client.list("/v3/settings/integrations/_search", {"filter": filter_}):
            yield Integration.model_validate(item)

    async def update(self, integration: Integration) -> Integration:
        """Update an integration's properties.
        Only `instance_name`, `params`, `state`, `collector_id` and `broker_id` are updatable.

        Args:
            integration: The integration to update.

        Returns:
            The updated integration.

        Raises:
            ResponseError: If an error occurs while communicating with the API.

        Example:
            ```python linenums="1" hl_lines="10"
            import asyncio

            from armis_sdk.clients.integrations_client import IntegrationsClient
            from armis_sdk.entities.integration import Integration


            async def main():
                integrations_client = IntegrationsClient()
                integration = Integration(id=1, state="INACTIVE")
                await integrations_client.update(integration)


            asyncio.run(main())
            ```
        """
        if integration.id is None:
            raise ArmisError("Can't update an integration without an id. Did you mean to call `.create(integration)`?")

        data = integration.model_dump(exclude=_READ_ONLY_FIELDS | {"name"}, exclude_none=True)

        if not data:
            return integration

        async with self._armis_client.client() as client:
            response = await client.patch(f"/v3/settings/integrations/{integration.id}", json=data)
            data = response_utils.get_data_dict(response)
            return Integration.model_validate(data)
