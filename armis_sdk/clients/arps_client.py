import datetime
import os
from typing import IO

import universalasync

from armis_sdk.core import response_utils
from armis_sdk.core.base_entity_client import BaseEntityClient
from armis_sdk.entities.arp_upload_result import ArpUploadResult


@universalasync.wrap
class ArpsClient(BaseEntityClient):
    """
    A client for uploading user ARP records.

    The primary entity for this client is [ArpUploadResult][armis_sdk.entities.arp_upload_result.ArpUploadResult].
    """

    async def upload(
        self,
        file: str | os.PathLike | IO[bytes],
        expiration: datetime.datetime,
        network_id: str,
    ) -> ArpUploadResult:
        """Upload a CSV of IP/MAC matches as user ARP records.

        Args:
            file: The path to (or a file-like object of) a CSV file with the columns `ip,mac`.
                The file can be at most 10MB.
            expiration: When the uploaded records expire. Must be in the future and at most 30 days from now.
            network_id: Identifies the logical network segment the ARP data originates from.

        Returns:
            An `ArpUploadResult` object summarizing the upload.

        Raises:
            ResponseError: If an error occurs while communicating with the API.

        Example:
            ```python linenums="1" hl_lines="10"
            import asyncio
            import datetime

            from armis_sdk.clients.arps_client import ArpsClient


            async def main():
                arps_client = ArpsClient()
                expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
                print(await arps_client.upload("/tmp/arps.csv", expiration, "L_621732956900298999"))


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            ArpUploadResult(total_rows=10, accepted_records=9, duplicate_rows=1, expiration=...)
            ```
        """
        data = {"expiration": expiration.isoformat(), "network_id": network_id}

        if not isinstance(file, (str, os.PathLike)):
            return await self._upload(file, data)

        with open(file, "rb") as opened:
            return await self._upload(opened, data)

    async def _upload(self, file: IO[bytes], data: dict[str, str]) -> ArpUploadResult:
        async with self._armis_client.client() as client:
            response = await client.post("/v3/arps", data=data, files={"file": ("arps.csv", file, "text/csv")})
            result = response_utils.get_data_dict(response)
            return ArpUploadResult.model_validate(result)
