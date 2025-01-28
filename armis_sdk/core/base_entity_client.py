import os
from typing import AsyncIterator
from typing import Optional
from typing import Type
from typing import Union

import httpx

from armis_sdk.core import response_utils
from armis_sdk.core.armis_client import ArmisClient
from armis_sdk.core.base_entity import BaseEntityT

ARMIS_CLIENT_ID = "ARMIS_CLIENT_ID"
ARMIS_PAGE_SIZE = "ARMIS_PAGE_SIZE"
ARMIS_SECRET_KEY = "ARMIS_SECRET_KEY"
ARMIS_TENANT = "ARMIS_TENANT"
DEFAULT_PAGE_LENGTH = 100


class BaseEntityClient:  # pylint: disable=too-few-public-methods

    def __init__(self, armis_client: Optional[ArmisClient] = None) -> None:
        self._armis_client = armis_client or ArmisClient()

    @classmethod
    def _get_data(cls, response: httpx.Response) -> Optional[Union[dict, list]]:
        response_utils.raise_for_status(response)
        parsed = response_utils.parse_response(response)
        return parsed.get("data")

    async def _paginate(
        self, url: str, key: str, model: Type[BaseEntityT]
    ) -> AsyncIterator[BaseEntityT]:
        page_size = int(os.getenv(ARMIS_PAGE_SIZE, str(DEFAULT_PAGE_LENGTH)))
        async with self._armis_client.client() as client:
            from_ = 0
            while from_ is not None:
                params = {"from": from_, "length": page_size}
                data = self._get_data(await client.get(url, params=params))
                items = data[key]
                for item in items:
                    yield model.model_validate(item)
                from_ = data.get("next")
