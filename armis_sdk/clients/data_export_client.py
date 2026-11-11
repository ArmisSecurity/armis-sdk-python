import asyncio
from collections.abc import AsyncIterator
from typing import Any

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
    async def disable(self, entity: type[BaseExportedEntity], time_frame_days: int | None = None):
        """Disable data export of the entity.

        Args:
            entity: The entity to disable exporting for.
            time_frame_days: The size of the exported time window, in days. Omit to use the entity's default.
                Each value is exported separately. See the API docs for the supported values per entity.

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

        Example:
            Each `time_frame_days` value is exported separately, so use the same value you passed to `enable()`:
            ```python linenums="1" hl_lines="9"
            import asyncio

            from armis_sdk.clients.data_export_client import DataExportClient
            from armis_sdk.entities.data_export.application import Application


            async def main():
                data_export_client = DataExportClient()
                await data_export_client.disable(Application, time_frame_days=7)


            asyncio.run(main())
            ```
        """
        await self.toggle(entity, False, time_frame_days)

    async def enable(self, entity: type[BaseExportedEntity], time_frame_days: int | None = None):
        """Enable data export of the entity.

        Args:
            entity: The entity to enable exporting for.
            time_frame_days: The size of the exported time window, in days. Omit to use the entity's default.
                Each value is exported separately. See the API docs for the supported values per entity.

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

        Example:
            Each `time_frame_days` value is exported separately, so a 7 days export is enabled (and later read) independently from a 30 days one:
            ```python linenums="1" hl_lines="9"
            import asyncio

            from armis_sdk.clients.data_export_client import DataExportClient
            from armis_sdk.entities.data_export.application import Application


            async def main():
                data_export_client = DataExportClient()
                await data_export_client.enable(Application, time_frame_days=7)


            asyncio.run(main())
            ```
        """
        await self.toggle(entity, True, time_frame_days)

    async def iterate(self, entity: type[T], time_frame_days: int | None = None, **kwargs: Any) -> AsyncIterator[T]:
        """Iterate over the exported data.

        Args:
            entity: The entity type to iterate over (must be a subclass of BaseExportedEntity).
            time_frame_days: The size of the time window to iterate over, in days. Omit to use the entity's default.
                Each value is exported separately. See the API docs for the supported values per entity.
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
                    filters=[("vendor", "in", ["Google", "Microsoft"])],
                ):
                    print(row.device_id, row.vendor, row.name, row.version)


            asyncio.run(main())
            ```

        Example:
            To iterate over the export of a specific time window (it must have been enabled with the same value):
            ```python linenums="1" hl_lines="9-10"
            import asyncio

            from armis_sdk.clients.data_export_client import DataExportClient
            from armis_sdk.entities.data_export.application import Application


            async def main():
                data_export_client = DataExportClient()
                async for row in data_export_client.iterate(Application, time_frame_days=7):
                    print(row.device_id)


            asyncio.run(main())
            ```
        """
        data_export = await self.get(entity, time_frame_days)
        if not data_export.enabled:
            raise ArmisError("Data export is disabled for this entity, please enable it first.")

        if data_export.file_format != "parquet":
            raise ArmisError("Only parquet files supported")

        for url in data_export.urls:
            data_frame: pandas.DataFrame = await asyncio.to_thread(pandas.read_parquet, url, **kwargs)
            for _, row in data_frame.iterrows():
                yield entity.series_to_model(row)

    async def get(self, entity: type[BaseExportedEntity], time_frame_days: int | None = None) -> DataExport:
        """Get the `DataExport` of the entity

        Args:
            entity: The entity to get the data for.
            time_frame_days: The size of the exported time window, in days. Omit to use the entity's default.
                Each value is exported separately. See the API docs for the supported values per entity.

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

        Example:
            To get the export of a specific time window:
            ```python linenums="1" hl_lines="9"
            import asyncio

            from armis_sdk.clients.data_export_client import DataExportClient
            from armis_sdk.entities.data_export.application import Application


            async def main():
                data_export_client = DataExportClient()
                print(await data_export_client.get(Application, time_frame_days=7))


            asyncio.run(main())
            ```
            Will output:
            ```python linenums="1"
            DataExport(...)
            ```
        """
        async with self._armis_client.client() as client:
            params = {"time_frame_days": time_frame_days} if time_frame_days is not None else None
            response = await client.get(f"/v3/data-export/{entity.entity_name}", params=params)
            data = response_utils.get_data_dict(response)
            return DataExport.model_validate(data)

    async def toggle(self, entity: type[BaseExportedEntity], enabled: bool, time_frame_days: int | None = None):
        """Enable / disable export of an entity.

        Args:
            entity: The entity to enable/disable exporting for.
            enabled: The new value to set.
            time_frame_days: The size of the exported time window, in days. Omit to use the entity's default.
                Each value is exported separately. See the API docs for the supported values per entity.

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

        Example:
            To toggle the export of a specific time window:
            ```python linenums="1" hl_lines="9"
            import asyncio

            from armis_sdk.clients.data_export_client import DataExportClient
            from armis_sdk.entities.data_export.application import Application


            async def main():
                data_export_client = DataExportClient()
                await data_export_client.toggle(Application, True, time_frame_days=7)


            asyncio.run(main())
            ```
        """
        data: dict[str, Any] = {"enabled": enabled}
        if time_frame_days is not None:
            data["time_frame_days"] = time_frame_days
        async with self._armis_client.client() as client:
            response = await client.patch(f"/v3/data-export/{entity.entity_name}", json=data)
            response_utils.raise_for_status(response)
