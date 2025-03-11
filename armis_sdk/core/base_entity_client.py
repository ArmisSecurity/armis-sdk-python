import os
from typing import AsyncIterator
from typing import Optional
from typing import Type
from typing import TypeVar

import httpx

from armis_sdk.core import response_utils
from armis_sdk.core.armis_client import ArmisClient
from armis_sdk.core.armis_error import ResponseError
from armis_sdk.core.base_entity import BaseEntityT

ARMIS_CLIENT_ID = "ARMIS_CLIENT_ID"
ARMIS_PAGE_SIZE = "ARMIS_PAGE_SIZE"
ARMIS_SECRET_KEY = "ARMIS_SECRET_KEY"
ARMIS_TENANT = "ARMIS_TENANT"
DEFAULT_PAGE_LENGTH = 100

DataTypeT = TypeVar("DataTypeT", dict, list)


class BaseEntityClient:  # pylint: disable=too-few-public-methods

    def __init__(self, armis_client: Optional[ArmisClient] = None) -> None:
        self._armis_client = armis_client or ArmisClient()

    @classmethod
    def _get_data(
        cls,
        response: httpx.Response,
        data_type: Type[DataTypeT],
    ) -> DataTypeT:
        response_utils.raise_for_status(response)
        parsed = response_utils.parse_response(response, dict)
        data = parsed.get("data")
        if not isinstance(data, data_type):
            raise ResponseError("Response data represents neither a dict nor a list.")
        return data

    @classmethod
    def _get_dict(cls, response: httpx.Response):
        return cls._get_data(response, dict)

    async def _paginate(
        self, url: str, key: str, model: Type[BaseEntityT]
    ) -> AsyncIterator[BaseEntityT]:
        page_size = int(os.getenv(ARMIS_PAGE_SIZE, str(DEFAULT_PAGE_LENGTH)))
        async with self._armis_client.client() as client:
            from_ = 0
            while from_ is not None:
                params = {"from": from_, "length": page_size}
                data = self._get_dict(await client.get(url, params=params))
                items = data[key]
                for item in items:
                    yield model.model_validate(item)
                from_ = data.get("next")
