import asyncio
from typing import Any
from typing import AsyncIterator
from typing import Type

import pandas
import universalasync

from armis_sdk.core import response_utils
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.core.base_entity_client import BaseEntityClient
from armis_sdk.entities.data_export.base_exported_entity import BaseExportedEntity
from armis_sdk.entities.data_export.base_exported_entity import T
from armis_sdk.entities.data_export.data_export import DataExport


@universalasync.wrap
class DataExportClient(BaseEntityClient):

    async def disable(self, entity: Type[BaseExportedEntity]):
        """Disable data export of the entity.

        Args:
            entity: The entity to disable exporting for.

        Example:
            ```python linenums="1" hl_lines="9"
            import asyncio

            from armis_sdk.clients.data_export_client import DataExportClient
            from armis_sdk.entities.data_export.application import Application


            async def main():
                data_export_client = DataExportClient()
                await data_export_client.disable(Application)

            asyncio.run(main())
            ```
        """
        await self.toggle(entity, False)

    async def enable(self, entity: Type[BaseExportedEntity]):
        """Enable data export of the entity.

        Args:
            entity: The entity to enable exporting for.

        Example:
            ```python linenums="1" hl_lines="9"
            import asyncio

            from armis_sdk.clients.data_export_client import DataExportClient
            from armis_sdk.entities.data_export.application import Application


            async def main():
                data_export_client = DataExportClient()
                await data_export_client.enable(Application)

            asyncio.run(main())
            ```
        """
        await self.toggle(entity, True)

    async def iterate(self, entity: Type[T], **kwargs: Any) -> AsyncIterator[T]:
        # pylint: disable=line-too-long
        """Iterate over the exported data.

        Args:
            entity: The entity type to iterate over (must be a subclass of BaseExportedEntity).
            **kwargs: Additional keyword arguments to pass to [pandas.read_parquet()](https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html).

        Returns:
            An (async) iterator of the underlying entity.

        Raises:
            ArmisError: If data export is disabled for the entity or if the file format is not parquet.

        Example:
            ```python linenums="1" hl_lines="9"
            import asyncio

            from armis_sdk.clients.data_export_client import DataExportClient
            from armis_sdk.entities.data_export.application import Application


            async def main():
                data_export_client = DataExportClient()
                async for row in data_export_client.iterate(Application):
                    print(type(row))

            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            <class 'armis_sdk.entities.data_export.application.Application'>
            <class 'armis_sdk.entities.data_export.application.Application'>
            <class 'armis_sdk.entities.data_export.application.Application'>
            ```

        Example:
            You can also pass additional parquet kwargs to filter columns or apply other parquet-specific operations:
            ```python linenums="1" hl_lines="9-13"
            import asyncio

            from armis_sdk.clients.data_export_client import DataExportClient
            from armis_sdk.entities.data_export.application import Application


            async def main():
                data_export_client = DataExportClient()
                async for row in data_export_client.iterate(
                    Application,
                    columns=["device_id", "vendor", "name", "version"],
                    filters=[("vendor", "in", ["Google", "Microsoft"])]
                ):
                    print(row.device_id, row.vendor, row.name, row.version)

            asyncio.run(main())
            ```
        """
        data_export = await self.get(entity)
        if not data_export.enabled:
            raise ArmisError(
                "Data export is disabled for this entity, please enable it first."
            )

        if data_export.file_format != "parquet":
            raise ArmisError("Only parquet files supported")

        for url in data_export.urls:
            data_frame: pandas.DataFrame = await asyncio.to_thread(
                pandas.read_parquet, url, **kwargs
            )
            for _, row in data_frame.iterrows():
                yield entity.series_to_model(row)

    async def get(self, entity: Type[BaseExportedEntity]) -> DataExport:
        """Get the `DataExport` of the entity

        Args:
            entity: The entity to get the data for.

        Returns:
            A `DataExport` object.

        Example:
            ```python linenums="1" hl_lines="9"
            import asyncio

            from armis_sdk.clients.data_export_client import DataExportClient
            from armis_sdk.entities.data_export.application import Application


            async def main():
                data_export_client = DataExportClient()
                print(await data_export_client.get(Application))

            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            DataExport(...)
            ```
        """
        async with self._armis_client.client() as client:
            response = await client.get(f"/v3/data-export/{entity.entity_name}")
            data = response_utils.get_data_dict(response)
            return DataExport.model_validate(data)

    async def toggle(self, entity: Type[BaseExportedEntity], enabled: bool):
        """Enable / disable export of an entity.

        Args:
            entity: The entity to enable/disable exporting for.
            enabled: The new value to set.

        Raises:
            ResponseError: If an error occurs while communicating with the API.

        Example:
            ```python linenums="1" hl_lines="9"
            import asyncio

            from armis_sdk.clients.data_export_client import DataExportClient
            from armis_sdk.entities.data_export.application import Application


            async def main():
                data_export_client = DataExportClient()
                await data_export_client.toggle(Application, True)

            asyncio.run(main())
            ```
        """
        data = {"enabled": enabled}
        async with self._armis_client.client() as client:
            response = await client.patch(
                f"/v3/data-export/{entity.entity_name}", json=data
            )
            response_utils.raise_for_status(response)
