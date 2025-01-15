import os
import importlib.metadata

from typing import Optional, Union, Type, AsyncIterator

import httpx

from armis_sdk.core.armis_auth import ArmisAuth
from armis_sdk.entities.base_entity import BaseEntityT

ARMIS_PAGE_SIZE = "ARMIS_PAGE_SIZE"
ARMIS_SECRET_KEY = "ARMIS_SECRET_KEY"
ARMIS_TENANT = "ARMIS_TENANT"
ARMIS_CLIENT_ID = "ARMIS_CLIENT_ID"
BASE_URL = "https://{tenant}.armis.com"
DEFAULT_PAGE_LENGTH = 100
VERSION = importlib.metadata.version("armis_sdk")


class ArmisClient:
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
        self._user_agent = f"ArmisPythonSDK/v{VERSION}"
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

    async def paginate(
        self, url: str, key: str, model: Type[BaseEntityT]
    ) -> AsyncIterator[BaseEntityT]:
        page_size = int(os.getenv(ARMIS_PAGE_SIZE, str(DEFAULT_PAGE_LENGTH)))
        async with self.client() as client:
            from_ = 0
            while from_ is not None:
                params = {"from": from_, "length": page_size}
                data = self._get_data(await client.get(url, params=params))
                items = data[key]
                for item in items:
                    yield model.model_validate(item)
                from_ = data.get("next")

    @classmethod
    def _get_data(cls, response: httpx.Response) -> Optional[Union[dict, list]]:
        response.raise_for_status()
        return response.json()["data"]
