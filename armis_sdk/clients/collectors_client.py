import contextlib
from typing import IO
from typing import AsyncIterator
from typing import Generator
from typing import Union

import httpx
import universalasync

from armis_sdk.core import response_utils
from armis_sdk.core.base_entity_client import BaseEntityClient
from armis_sdk.entities.collector_image import CollectorImage
from armis_sdk.entities.download_progress import DownloadProgress
from armis_sdk.types.collector_image_type import CollectorImageType


@universalasync.wrap
class CollectorsClient(BaseEntityClient):
    # pylint: disable=line-too-long
    """
    A client for interacting with Armis collectors.

    The primary entity for this client is [CollectorImage][armis_sdk.entities.collector_image.CollectorImage].
    """

    async def download_image(
        self,
        destination: Union[str, IO[bytes]],
        image_type: CollectorImageType = "OVA",
    ) -> AsyncIterator[DownloadProgress]:
        """Download a collector image to a specified destination path / file.

        Args:
            destination: The file path or file-like object where the collector image will be saved.
            image_type: The type of collector image to download. Defaults to "OVA".

        Returns:
            An (async) iterator of `DownloadProgress` object.

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
                # pylint: disable-next=contextmanager-generator-missing-cleanup
                with self.open_file(destination) as file:
                    async for chunk in response.aiter_bytes():
                        file.write(chunk)
                        yield DownloadProgress(downloaded=file.tell(), total=total_size)

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
            response = await client.get(
                "/v3/collectors/_image", params={"image_type": image_type}
            )
            data = response_utils.get_data_dict(response)
            return CollectorImage.model_validate(data)

    @classmethod
    @contextlib.contextmanager
    def open_file(
        cls, destination: Union[str, IO[bytes]]
    ) -> Generator[IO[bytes], None, None]:
        if isinstance(destination, str):
            with open(destination, "wb") as file:
                yield file
        else:
            yield destination
