import importlib.metadata
import os
import platform
from typing import AsyncIterator
from typing import Optional
from typing import TypeVar

import httpx
import universalasync
from httpx_retries import Retry
from httpx_retries import RetryTransport

from armis_sdk.core import response_utils
from armis_sdk.core.armis_auth import ArmisAuth
from armis_sdk.core.client_credentials import ClientCredentials

API_BASE_URL = "https://api.armis.com"
ARMIS_CLIENT_ID = "ARMIS_CLIENT_ID"
ARMIS_CLIENT_SECRET = "ARMIS_CLIENT_SECRET"
ARMIS_PAGE_SIZE = "ARMIS_PAGE_SIZE"
ARMIS_REQUEST_BACKOFF = "ARMIS_REQUEST_BACKOFF"
ARMIS_REQUEST_RETRIES = "ARMIS_REQUEST_RETRIES"
ARMIS_SCOPES = "ARMIS_SCOPES"
ARMIS_AUDIENCE = "ARMIS_AUDIENCE"
ARMIS_VENDOR_ID = "ARMIS_VENDOR_ID"
DEFAULT_PAGE_LENGTH = 100
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
    A class that provides easy access to the Armis API, taking care of:

    1. Authenticating requests.
    2. Retrying of failed requests (when applicable).
    3. Pagination of requests (when applicable).
    4. Proxy configuration via HTTPS_PROXY and HTTP_PROXY environment variables.
    """

    def __init__(self, credentials: Optional[ClientCredentials] = None):
        credentials = self._get_credentials(credentials)
        self._auth = ArmisAuth(API_BASE_URL, credentials)
        self._user_agent = " ".join(USER_AGENT_PARTS)
        try:
            self._default_retries = int(os.getenv(ARMIS_REQUEST_RETRIES, "3"))
        except ValueError:
            self._default_retries = 0
        try:
            self._default_backoff = float(os.getenv(ARMIS_REQUEST_BACKOFF, "0.5"))
        except ValueError:
            self._default_backoff = 0

    def client(self, retries: Optional[int] = None, backoff: Optional[float] = None):
        retries = retries if retries is not None else self._default_retries
        backoff = backoff if backoff is not None else self._default_backoff
        retry = Retry(total=retries, backoff_factor=backoff)

        if proxy := self._get_proxy_config():
            http_transport = httpx.AsyncHTTPTransport(proxy=proxy)
            transport = RetryTransport(retry=retry, transport=http_transport)
        else:
            transport = RetryTransport(retry=retry)

        return httpx.AsyncClient(
            auth=self._auth,
            base_url=API_BASE_URL,
            headers={
                "User-Agent": self._user_agent,
            },
            transport=transport,
            trust_env=True,
        )

    async def list(self, url: str, body: Optional[dict] = None) -> AsyncIterator[dict]:
        """List all items from a paginated endpoint.

        Args:
            url (str): The relative endpoint URL.
            body (dict): Payload to send as POST request.

        Returns:
            An (async) iterator of `dict`s.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.core.armis_client import ArmisClient


            async def main():
                armis_client = ArmisClient()
                async for item in armis_client.list("/v3/settings/sites"):
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
            params = {"limit": page_size, **(body or {})}
            while True:
                if body:
                    response = await client.post(url, json=params)
                else:
                    response = await client.get(url, params=params)
                data = response_utils.get_data_dict(response)
                items = data["items"]
                for item in items:
                    yield item
                if next_ := data.get("next"):
                    params["after"] = next_
                else:
                    break

    @classmethod
    def _get_credentials(
        cls, credentials: Optional[ClientCredentials]
    ) -> ClientCredentials:
        credentials = credentials or ClientCredentials()
        credentials.vendor_id = credentials.vendor_id or os.getenv(ARMIS_VENDOR_ID)
        credentials.audience = credentials.audience or os.getenv(ARMIS_AUDIENCE)
        credentials.client_id = credentials.client_id or os.getenv(ARMIS_CLIENT_ID)
        credentials.client_secret = credentials.client_secret or os.getenv(
            ARMIS_CLIENT_SECRET
        )
        env_scopes = os.getenv(ARMIS_SCOPES)
        credentials.scopes = credentials.scopes or (
            env_scopes.split(",") if env_scopes else []
        )

        if not credentials.audience:
            raise ValueError(
                f"Either populate the {ARMIS_AUDIENCE!r} environment variable "
                "or pass an explicit value to the ClientCredentials class"
            )
        if not credentials.client_id:
            raise ValueError(
                f"Either populate the {ARMIS_CLIENT_ID!r} environment variable "
                "or pass an explicit value to the ClientCredentials class"
            )
        if not credentials.client_secret:
            raise ValueError(
                f"Either populate the {ARMIS_CLIENT_SECRET!r} environment variable "
                "or pass an explicit value to the ClientCredentials class"
            )
        if not credentials.scopes:
            raise ValueError(
                f"Either populate the {ARMIS_SCOPES!r} environment variable "
                "or pass an explicit value to the ClientCredentials class"
            )
        if not credentials.vendor_id:
            raise ValueError(
                f"Either populate the {ARMIS_VENDOR_ID!r} environment variable "
                "or pass an explicit value to the ClientCredentials class"
            )

        return credentials

    @classmethod
    def _get_proxy_config(cls):
        """Get proxy configuration from environment variables."""
        return os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
