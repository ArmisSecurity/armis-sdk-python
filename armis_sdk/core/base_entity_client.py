from __future__ import annotations

from typing import Optional
from typing import Type  # noqa: UP035  # TODO: fix UP035 (deprecated import, use updated module)
from typing import TYPE_CHECKING

import universalasync

from armis_sdk.core.armis_client import ArmisClient
from armis_sdk.core.base_entity import BaseEntityT


if TYPE_CHECKING:
    from collections.abc import AsyncIterator


class BaseEntityClient:
    def __init__(self, armis_client: ArmisClient | None = None) -> None:
        self._armis_client = armis_client or ArmisClient()

    @universalasync.async_to_sync_wraps
    async def _list(self, url: str, model: type[BaseEntityT]) -> AsyncIterator[BaseEntityT]:
        async for item in self._armis_client.list(url):
            yield model.model_validate(item)
