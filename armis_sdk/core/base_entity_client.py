from typing import AsyncIterator
from typing import Optional
from typing import Type

import universalasync

from armis_sdk.core.armis_client import ArmisClient
from armis_sdk.core.base_entity import BaseEntityT


class BaseEntityClient:  # pylint: disable=too-few-public-methods

    def __init__(self, armis_client: Optional[ArmisClient] = None) -> None:
        self._armis_client = armis_client or ArmisClient()

    @universalasync.async_to_sync_wraps
    async def _list(
        self, url: str, key: str, model: Type[BaseEntityT]
    ) -> AsyncIterator[BaseEntityT]:
        async for item in self._armis_client.list(url, key):
            yield model.model_validate(item)
