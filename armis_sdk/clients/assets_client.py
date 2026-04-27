from __future__ import annotations

import datetime
from typing import Optional
from typing import Type  # noqa: UP035  # TODO: fix UP035 (deprecated import, use updated module)
from typing import TYPE_CHECKING
from typing import Union

import universalasync

from armis_sdk.core import response_utils
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.core.armis_error import BulkUpdateError
from armis_sdk.core.armis_error import BulkUpdateItemError
from armis_sdk.core.base_entity_client import BaseEntityClient
from armis_sdk.entities.asset import Asset
from armis_sdk.entities.asset import AssetT
from armis_sdk.entities.asset_field_description import AssetFieldDescription
from armis_sdk.entities.device import Device
from armis_sdk.types.asset_id_source import AssetIdSource


if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@universalasync.wrap
class AssetsClient(BaseEntityClient):
    """
    A client for interacting with assets.

    The primary entities for this client inherit from [Asset][armis_sdk.entities.asset.Asset]:

    1. [Device][armis_sdk.entities.device.Device]
    """

    async def list_by_asset_id(
        self,
        asset_class: type[AssetT],
        asset_ids: list[int] | list[str],
        asset_id_source: AssetIdSource = "ASSET_ID",
        fields: list[str] | None = None,
    ) -> AsyncIterator[AssetT]:
        """List assets by asset ID or other identifiers.

        Args:
            asset_class: The asset class to list. Must inherit from [Asset][armis_sdk.entities.asset.Asset].
            asset_ids: A list of asset identifiers (int or str depending on asset_id_source).
            asset_id_source: The type of identifier provided in asset_ids.
            fields: Optional list of fields to retrieve. If None, all non-custom fields are retrieved.

        Yields:
            Assets of the specified class matching the provided identifiers.

        Example:
            ```python linenums="1" hl_lines="14 18"
            import asyncio

            from armis_sdk.clients.assets_client import AssetsClient
            from armis_sdk.entities.device import Device


            async def main():
                assets_client = AssetsClient()

                device_ids = [1, 2, 3]
                ipv4_addresses = ["1.1.1.1", "2.2.2.2", "3.3.3.3"]

                # List by the default source "ASSET_ID"
                async for device in assets_client.list_by_asset_id(Device, device_ids):
                    print(device)

                # List by explicit source "IPV4_ADDRESS"
                async for device in assets_client.list_by_asset_id(Device, ipv4_addresses, asset_id_source="IPV4_ADDRESS"):
                    print(device)


            asyncio.run(main())
            ```
        """
        if not asset_ids:
            raise ArmisError("asset_ids must not be empty")
        filter_ = {
            "filter_criteria": "ASSET_ID",
            "asset_ids": asset_ids,
            "asset_id_source": asset_id_source,
        }
        async for item in self._list_assets(asset_class, fields, filter_):
            yield item

    async def list_by_boundary_id(
        self,
        asset_class: type[AssetT],
        boundary_ids: list[int],
        fields: list[str] | None = None,
    ) -> AsyncIterator[AssetT]:
        """List assets by boundary ID.

        Args:
            asset_class: The asset class to list. Must inherit from [Asset][armis_sdk.entities.asset.Asset].
            boundary_ids: A list of boundary IDs to filter by.
            fields: Optional list of fields to retrieve. If None, all non-custom fields are retrieved.

        Yields:
            Assets of the specified class belonging to any of the provided boundaries.

        Example:
            ```python linenums="1" hl_lines="10"
            import asyncio

            from armis_sdk.clients.assets_client import AssetsClient
            from armis_sdk.entities.device import Device


            async def main():
                assets_client = AssetsClient()

                async for device in assets_client.list_by_boundary_id(Device, [1, 2, 3]):
                    print(device)


            asyncio.run(main())
            ```
        """
        filter_ = self._build_boundary_id_filter(boundary_ids)
        async for item in self._list_assets(asset_class, fields, filter_):
            yield item

    async def list_by_last_seen(
        self,
        asset_class: type[AssetT],
        last_seen: datetime.datetime | datetime.timedelta,
        fields: list[str] | None = None,
    ) -> AsyncIterator[AssetT]:
        """List assets by last seen timestamp.

        Args:
            asset_class: The asset class to list. Must inherit from [Asset][armis_sdk.entities.asset.Asset].
            last_seen: Either a datetime (assets seen on or after this time) or timedelta (assets seen within this duration).
            fields: Optional list of fields to retrieve. If None, all non-custom fields are retrieved.

        Yields:
            Assets of the specified class matching the last seen criteria.

        Raises:
            ArmisError: If last_seen is neither datetime nor timedelta.

        Example:
            ```python linenums="1" hl_lines="12 16"
            import asyncio
            import datetime

            from armis_sdk.clients.assets_client import AssetsClient
            from armis_sdk.entities.device import Device


            async def main():
                assets_client = AssetsClient()

                # List devices seen in the last 24 hours
                async for device in assets_client.list_by_last_seen(Device, datetime.timedelta(days=1)):
                    print(device)

                # List devices seen on or after December 8, 2025
                async for device in assets_client.list_by_last_seen(Device, datetime.datetime(2025, 12, 8)):
                    print(device)


            asyncio.run(main())
            ```
        """
        filter_ = self._build_last_seen_filter(last_seen)
        async for item in self._list_assets(asset_class, fields, filter_):
            yield item

    async def list_by_multiple(
        self,
        asset_class: type[AssetT],
        last_seen: datetime.datetime | datetime.timedelta | None = None,
        site_ids: list[int] | None = None,
        boundary_ids: list[int] | None = None,
        fields: list[str] | None = None,
    ) -> AsyncIterator[AssetT]:
        """List assets matching multiple filter criteria simultaneously (AND logic).

        At least one of `last_seen`, `site_ids`, or `boundary_ids` must be provided.
        Each criterion that is provided is applied as an AND condition.

        Args:
            asset_class: The asset class to list. Must inherit from [Asset][armis_sdk.entities.asset.Asset].
            last_seen: Either a datetime (assets seen on or after this time) or timedelta (assets seen within this duration).
            site_ids: A list of site IDs to filter by.
            boundary_ids: A list of boundary IDs to filter by.
            fields: Optional list of fields to retrieve. If None, all non-custom fields are retrieved.

        Yields:
            Assets of the specified class matching all provided criteria.

        Raises:
            ArmisError: If no filter criteria are provided, or if last_seen is an invalid type.

        Example:
            ```python linenums="1" hl_lines="11-15"
            import asyncio
            import datetime

            from armis_sdk.clients.assets_client import AssetsClient
            from armis_sdk.entities.device import Device


            async def main():
                assets_client = AssetsClient()

                async for device in assets_client.list_by_multiple(
                    Device,
                    site_ids=[1, 2],
                    last_seen=datetime.timedelta(hours=1),
                ):
                    print(device)


            asyncio.run(main())
            ```
        """
        filters = []

        if last_seen is not None:
            filters.append(self._build_last_seen_filter(last_seen))

        if site_ids is not None:
            filters.append(self._build_site_id_filter(site_ids))

        if boundary_ids is not None:
            filters.append(self._build_boundary_id_filter(boundary_ids))

        if not filters:
            raise ArmisError("At least one of filter must be provided")

        filter_ = {
            "filter_criteria": "MULTIPLE",
            "filters": filters,
        }
        async for item in self._list_assets(asset_class, fields, filter_):
            yield item

    async def list_by_site_id(
        self,
        asset_class: type[AssetT],
        site_ids: list[int],
        fields: list[str] | None = None,
    ) -> AsyncIterator[AssetT]:
        """List assets by site ID.

        Args:
            asset_class: The asset class to list. Must inherit from [Asset][armis_sdk.entities.asset.Asset].
            site_ids: A list of site IDs to filter by.
            fields: Optional list of fields to retrieve. If None, all non-custom fields are retrieved.

        Yields:
            Assets of the specified class belonging to any of the provided sites.

        Example:
            ```python linenums="1" hl_lines="10"
            import asyncio

            from armis_sdk.clients.assets_client import AssetsClient
            from armis_sdk.entities.device import Device


            async def main():
                assets_client = AssetsClient()

                async for device in assets_client.list_by_site_id(Device, [1, 2, 3]):
                    print(device)


            asyncio.run(main())
            ```
        """
        filter_ = self._build_site_id_filter(site_ids)
        async for item in self._list_assets(asset_class, fields, filter_):
            yield item

    async def list_fields(self, asset_class: type[AssetT]) -> AsyncIterator[AssetFieldDescription]:
        """List all available fields for a given asset class.

        Args:
            asset_class: The asset class to list fields for. Must inherit from [Asset][armis_sdk.entities.asset.Asset].

        Yields:
            Field descriptions including field name, type, and other metadata.

        Example:
            ```python linenums="1" hl_lines="10"
            import asyncio

            from armis_sdk.clients.assets_client import AssetsClient
            from armis_sdk.entities.device import Device


            async def main():
                assets_client = AssetsClient()

                async for field in assets_client.list_fields(Device):
                    print(f"{field.name}: {field.type}")


            asyncio.run(main())
            ```
        """
        async with self._armis_client.client() as client:
            response = await client.get(
                "/v3/assets/_search/fields",
                params={"asset_type": asset_class.asset_type},
            )
            data = response_utils.get_data_dict(response)
            for item in data["items"]:
                yield AssetFieldDescription.model_validate(item)

    async def update(
        self,
        assets: list[AssetT],
        fields: list[str],
        asset_id_source: AssetIdSource = "ASSET_ID",
    ) -> None:
        """Bulk update assets.

        Args:
            assets: A list of assets. Items must inherit from [Asset][armis_sdk.entities.asset.Asset].
            fields: A list of fields to update. Currently only custom properties are supported (i.e.  `custom.MyField`).
            asset_id_source: From where on the asset to take the unique identifier.

        Raises:
            BulkUpdateError: If an error occurs while trying to update any of the assets.

        Example:
            ```python linenums="1" hl_lines="13 16"
            import asyncio

            from armis_sdk.clients.assets_client import AssetsClient
            from armis_sdk.entities.device import Device


            async def main():
                assets_client = AssetsClient()

                device = Device(device_id=1, ipv4_addresses=["1.2.3.4"], custom={"MyField": "Hello, World"})

                # Update based on the default source "ASSET_ID"
                await assets_client.update([device], ["custom.MyField"])

                # Update based on the explicit source "IPV4_ADDRESS"
                await assets_client.update([device], ["custom.MyField"], asset_id_source="IPV4_ADDRESS")


            asyncio.run(main())
            ```
        """
        if not assets or not fields:
            return

        self._validate_asset_class(assets)

        asset_class = type(assets[0])
        self._validate_fields(asset_class, fields, allow_model_members=False)

        items = []
        for index, asset in enumerate(assets):
            asset_id = self._get_asset_id(asset, index, asset_id_source)
            for field in fields:
                items.append(self._create_bulk_update_request(asset, asset_id, field))

        if not items:
            return

        payload = {
            "items": items,
            "asset_type": asset_class.asset_type,
            "asset_id_source": asset_id_source,
        }
        async with self._armis_client.client() as client:
            response = await client.post("/v3/assets/_bulk", json=payload)
            data = response_utils.get_data_dict(response)
            errors = [
                BulkUpdateItemError(index=index, request=items[index], response=item)
                for index, item in enumerate(data["items"])
                if item["status"] != 202
            ]
            if errors:
                raise BulkUpdateError(errors)

    @staticmethod
    def _build_boundary_id_filter(boundary_ids: list[int]) -> dict:
        if not boundary_ids:
            raise ArmisError("boundary_ids must not be empty")
        return {"filter_criteria": "BOUNDARY_ID", "boundary_ids": boundary_ids}

    @staticmethod
    def _build_last_seen_filter(last_seen: datetime.datetime | datetime.timedelta) -> dict:
        filter_: dict[str, str | int] = {"filter_criteria": "LAST_SEEN"}
        if isinstance(last_seen, datetime.datetime):
            filter_["last_seen_ge"] = last_seen.isoformat()
        elif isinstance(last_seen, datetime.timedelta):
            filter_["last_seen_seconds"] = int(last_seen.total_seconds())
        else:
            raise ArmisError(f"Invalid 'last_seen' type {type(last_seen)}")
        return filter_

    @staticmethod
    def _build_site_id_filter(site_ids: list[int]) -> dict:
        if not site_ids:
            raise ArmisError("site_ids must not be empty")
        return {"filter_criteria": "SITE_ID", "site_ids": site_ids}

    @classmethod
    def _create_bulk_update_request(
        cls,
        asset: Asset,
        asset_id: str | int,
        field: str,
    ):
        request = {"asset_id": asset_id, "key": field}
        if cls._is_custom_field(field):
            key = field.split(".", 1)[1]
            if value := asset.custom.get(key):
                request["operation"] = "SET"
                request["value"] = value
            else:
                request["operation"] = "UNSET"
        else:
            raise ArmisError(f"Updating the field {field!r} is currently not supported")

        return request

    @classmethod
    def _get_asset_id(
        cls,
        asset: Asset,
        index: int,
        asset_id_source: AssetIdSource,
    ) -> str | int:
        if isinstance(asset, Device):
            return cls._get_device_asset_id(asset, index, asset_id_source)

        raise ArmisError(f"Can't get {asset_id_source} of asset {asset!r}")

    @classmethod
    def _get_device_asset_id(
        cls,
        device: Device,
        index: int,
        asset_id_source: AssetIdSource,
    ):
        if asset_id_source == "ASSET_ID":
            if device.device_id is None:
                raise ArmisError(f"Device at index {index} doesn't have a device id")
            return device.device_id

        if asset_id_source == "MAC_ADDRESS":
            if device.mac_addresses is None or len(device.mac_addresses) != 1:
                raise ArmisError(f"Device at index {index} doesn't have exactly one mac address")
            return device.mac_addresses[0]

        if asset_id_source == "IPV4_ADDRESS":
            if device.ipv4_addresses is None or len(device.ipv4_addresses) != 1:
                raise ArmisError(f"Device at index {index} doesn't have exactly one IPv4 address")
            return device.ipv4_addresses[0]

        if asset_id_source == "IPV6_ADDRESS":
            if device.ipv6_addresses is None or len(device.ipv6_addresses) != 1:
                raise ArmisError(f"Device at index {index} doesn't have exactly one IPv6 address")
            return device.ipv6_addresses[0]

        if asset_id_source == "SERIAL_NUMBER":
            if device.serial_numbers is None or len(device.serial_numbers) != 1:
                raise ArmisError(f"Device at index {index} doesn't have exactly one serial number")
            return device.serial_numbers[0]

        raise ArmisError(f"Can't get {asset_id_source!r} of device at index {index}")

    @classmethod
    def _is_custom_field(cls, field: str) -> bool:
        return field.startswith("custom.")

    @classmethod
    def _is_integration_field(cls, field: str) -> bool:
        return field.startswith("integration.")

    async def _list_assets(
        self,
        asset_class: type[AssetT],
        fields: list[str] | None,
        filter_: dict,
    ) -> AsyncIterator[AssetT]:
        fields = fields or sorted(asset_class.all_fields())

        self._validate_fields(asset_class, fields)

        body = {
            "asset_type": asset_class.asset_type,
            "fields": fields,
            "filter": filter_,
        }
        async for item in self._armis_client.list("/v3/assets/_search", body=body, after_location="filter"):
            yield asset_class.from_search_result(item)

    @classmethod
    def _validate_asset_class(cls, assets: list[AssetT]):
        asset_types = {type(asset) for asset in assets}
        if len(asset_types) > 1:
            asset_types_str = ", ".join(sorted(repr(at.__name__) for at in asset_types))
            raise ArmisError(f"All assets must be of the same type, got {len(asset_types)} types: {asset_types_str}")

    @classmethod
    def _validate_fields(
        cls,
        asset_class: type[AssetT],
        fields: list[str],
        allow_model_members=True,
    ):
        invalid_fields = []
        all_fields = asset_class.all_fields()
        for field in fields:
            if cls._is_custom_field(field):
                continue

            if cls._is_integration_field(field):
                continue

            if allow_model_members and field in all_fields:
                continue

            invalid_fields.append(field)

        if invalid_fields:
            fields_str = ", ".join(map(repr, invalid_fields))
            raise ArmisError(f"The following fields are not supported with this operation: {fields_str}")
