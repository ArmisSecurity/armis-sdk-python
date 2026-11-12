from collections.abc import AsyncIterator
from collections.abc import Generator
import contextlib
from typing import IO

import httpx
import universalasync

from armis_sdk.core import response_utils
from armis_sdk.core.base_entity_client import BaseEntityClient
from armis_sdk.entities.collector import Collector
from armis_sdk.entities.collector_image import CollectorImage
from armis_sdk.entities.download_progress import DownloadProgress
from armis_sdk.types.collector_image_type import CollectorImageType


@universalasync.wrap
class CollectorsClient(BaseEntityClient):
    """
    A client for interacting with Armis collectors.

    The primary entities for this client are [Collector][armis_sdk.entities.collector.Collector] and
    [CollectorImage][armis_sdk.entities.collector_image.CollectorImage].
    """

    async def download_image(
        self,
        destination: str | IO[bytes],
        image_type: CollectorImageType = "OVA",
    ) -> AsyncIterator[DownloadProgress]:
        """Download a collector image to a specified destination path or file.

        Args:
            destination: The file path or file-like object where the collector image will be saved.
            image_type: The type of collector image to download. Defaults to "OVA".

        Returns:
            An (async) iterator of `DownloadProgress` objects.

        Example:
            ```python linenums="1" hl_lines="10 15"
            import asyncio

            from armis_sdk.clients.collectors_client import CollectorsClient


            async def main():
                collectors_client = CollectorsClient()

                # Download to a path
                async for progress in armis_sdk.collectors.download_image("/tmp/collector.ova"):
                    print(progress.percent)

                # Download to a file
                with open("/tmp/collector.ova", "wb") as file:
                    async for progress in armis_sdk.collectors.download_image(file):
                        print(progress.percent)


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            1%
            2%
            3%
            ```
            etc.
        """
        collector_image = await self.get_image(image_type=image_type)
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", collector_image.url) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("Content-Length", "0"))
                with self.open_file(destination) as file:
                    async for chunk in response.aiter_bytes():
                        file.write(chunk)
                        yield DownloadProgress(downloaded=file.tell(), total=total_size)

    async def get(self, collector_number: int) -> Collector:
        """Get a `Collector` by its number.

        Args:
            collector_number: The number of the collector to get.

        Returns:
            A `Collector` object.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.collectors_client import CollectorsClient


            async def main():
                collectors_client = CollectorsClient()
                print(await collectors_client.get(1))


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Collector(collector_number=1, name="...", ...)
            ```
        """
        async with self._armis_client.client() as client:
            response = await client.get(f"/v3/collectors/{collector_number}")
            data = response_utils.get_data_dict(response)
            return Collector.model_validate(data)

    async def get_image(self, image_type: CollectorImageType = "OVA") -> CollectorImage:
        """Get collector image information including download URL and credentials.

        Args:
            image_type: The type of collector image to retrieve. Defaults to "OVA".

        Returns:
            A `CollectorImage` object.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.collectors_client import CollectorsClient


            async def main():
                collectors_client = CollectorsClient()
                print(await collectors_client.get_image(image_type="OVA"))


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            CollectorImage(url="...", ...)
            ```
        """
        async with self._armis_client.client() as client:
            response = await client.get("/v3/collectors/_image", params={"image_type": image_type})
            data = response_utils.get_data_dict(response)
            return CollectorImage.model_validate(data)

    async def list(self) -> AsyncIterator[Collector]:
        """List all the tenant's collectors.
        This method takes care of pagination, so you don't have to deal with it.

        Returns:
            An (async) iterator of `Collector` objects.

        Example:
            ```python linenums="1" hl_lines="8"
            import asyncio

            from armis_sdk.clients.collectors_client import CollectorsClient


            async def main():
                collectors_client = CollectorsClient()
                async for collector in collectors_client.list():
                    print(collector)


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            Collector(collector_number=1, name="...", ...)
            Collector(collector_number=2, name="...", ...)
            ```
        """
        async for item in self._list("/v3/collectors", Collector):
            yield item

    @classmethod
    @contextlib.contextmanager
    def open_file(cls, destination: str | IO[bytes]) -> Generator[IO[bytes], None, None]:
        if isinstance(destination, str):
            with open(destination, "wb") as file:
                yield file
        else:
            yield destination
