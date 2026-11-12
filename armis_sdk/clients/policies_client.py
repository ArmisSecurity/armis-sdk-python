from collections.abc import AsyncIterator

import universalasync

from armis_sdk.core.base_entity_client import BaseEntityClient
from armis_sdk.entities.policy import Policy


@universalasync.wrap
class PoliciesClient(BaseEntityClient):
    """
    A client for interacting with policies.

    The primary entity for this client is [Policy][armis_sdk.entities.policy.Policy].
    """

    async def list(self) -> AsyncIterator[Policy]:
        """List all the tenant's policies.
        This method takes care of pagination, so you don't have to deal with it.

        Returns:
            An (async) iterator of `Policy` objects.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.policies_client import PoliciesClient


            async def main():
                policies_client = PoliciesClient()
                async for policy in policies_client.list():
                    print(policy)


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Policy(id=1, name="...", ...)
            Policy(id=2, name="...", ...)
            ```
        """
        async for item in self._list("/v3/policies", Policy):
            yield item
