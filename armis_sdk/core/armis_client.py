import importlib.metadata
import os
import platform
from typing import AsyncIterator
from typing import Optional
from typing import TypeVar

import httpx
import universalasync

from armis_sdk.core import response_utils
from armis_sdk.core.armis_auth import ArmisAuth

ARMIS_PAGE_SIZE = "ARMIS_PAGE_SIZE"
ARMIS_SECRET_KEY = "ARMIS_SECRET_KEY"
ARMIS_TENANT = "ARMIS_TENANT"
ARMIS_CLIENT_ID = "ARMIS_CLIENT_ID"
BASE_URL = "https://{tenant}.armis.com"
DEFAULT_PAGE_LENGTH = 1000
try:
    VERSION = importlib.metadata.version("armis_sdk")
except importlib.metadata.PackageNotFoundError:
    VERSION = "unknown"

USER_AGENT_PARTS = [
    f"Python/{platform.python_version()}",
    httpx.Client().headers.get("User-Agent"),
    f"ArmisPythonSDK/v{VERSION}",
]
DataTypeT = TypeVar("DataTypeT", dict, list)


@universalasync.wrap
class ArmisClient:  # pylint: disable=too-few-public-methods
    """
    A class that provides easy access to the Armis API, taking care of authenticating requests.
    """

    def __init__(
        self,
        tenant: Optional[str] = None,
        secret_key: Optional[str] = None,
        client_id: Optional[str] = None,
    ):
        tenant = os.getenv(ARMIS_TENANT, tenant)
        secret_key = os.getenv(ARMIS_SECRET_KEY, secret_key)
        client_id = os.getenv(ARMIS_CLIENT_ID, client_id)

        if not tenant:
            raise ValueError(
                f"Either populate the {ARMIS_TENANT!r} environment variable "
                f"or pass an explicit value to the constructor"
            )
        if not secret_key:
            raise ValueError(
                f"Either populate the {ARMIS_SECRET_KEY!r} environment variable "
                f"or pass an explicit value to the constructor"
            )
        if not client_id:
            raise ValueError(
                f"Either populate the {ARMIS_CLIENT_ID!r} environment variable "
                f"or pass an explicit value to the constructor"
            )

        self._base_url = BASE_URL.format(tenant=tenant)
        self._auth = ArmisAuth(self._base_url, secret_key)
        self._user_agent = " ".join(USER_AGENT_PARTS)
        self._client_id = client_id

    def client(self):
        return httpx.AsyncClient(
            auth=self._auth,
            base_url=self._base_url,
            headers={
                "User-Agent": self._user_agent,
                "Armis-API-Client-Id": self._client_id,
            },
        )

    async def list(self, url: str, key: str) -> AsyncIterator[dict]:
        """List all items from a paginated endpoint.

        Args:
            url (str): The relative endpoint URL.
            key (str): The key inside the data object that contains the items.

        Returns:
            An (async) iterator of `dict`s.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.core.armis_client import ArmisClient


            async def main():
                armis_client = ArmisClient()
                async for item in armis_client.list("/api/v1/sites/", "sites"):
                    print(item)

            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            {...}
            {...}
            ```
        """
        page_size = int(os.getenv(ARMIS_PAGE_SIZE, str(DEFAULT_PAGE_LENGTH)))
        async with self.client() as client:
            from_ = 0
            while from_ is not None:
                params = {"from": from_, "length": page_size}
                response = await client.get(url, params=params)
                data = response_utils.get_data_dict(response)
                items = data[key]
                for item in items:
                    yield item
                from_ = data.get("next")
