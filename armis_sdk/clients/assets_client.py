import datetime
from typing import AsyncIterator
from typing import Optional
from typing import Type
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


@universalasync.wrap
class AssetsClient(BaseEntityClient):  # pylint: disable=too-few-public-methods
    # pylint: disable=line-too-long
    """
    A client for interacting with assets.

    The primary entities for this client inherit from [Asset][armis_sdk.entities.asset.Asset]:

    1. [Device][armis_sdk.entities.device.Device]
    """

    async def list_by_asset_id(
        self,
        asset_class: Type[AssetT],
        asset_ids: Union[list[int], list[str]],
        asset_id_source: AssetIdSource = "ASSET_ID",
        fields: Optional[list[str]] = None,
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
            ```python linenums="1" hl_lines="13 17"
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
        filter_ = {
            "filter_criteria": "ASSET_ID",
            "asset_ids": asset_ids,
            "asset_id_source": asset_id_source,
        }
        async for item in self._list_assets(asset_class, fields, filter_):
            yield item

    async def list_by_last_seen(
        self,
        asset_class: Type[AssetT],
        last_seen: Union[datetime.datetime, datetime.timedelta],
        fields: Optional[list[str]] = None,
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
            ```python linenums="1" hl_lines="11 15"
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
        filter_: dict[str, Union[str, int]] = {"filter_criteria": "LAST_SEEN"}

        if isinstance(last_seen, datetime.datetime):
            filter_["last_seen_ge"] = last_seen.isoformat()
        elif isinstance(last_seen, datetime.timedelta):
            filter_["last_seen_seconds"] = int(last_seen.total_seconds())
        else:
            raise ArmisError(f"Invalid 'last_seen' type {type(last_seen)}")

        async for item in self._list_assets(asset_class, fields, filter_):
            yield item

    async def list_fields(
        self, asset_class: Type[AssetT]
    ) -> AsyncIterator[AssetFieldDescription]:
        """List all available fields for a given asset class.

        Args:
            asset_class: The asset class to list fields for. Must inherit from [Asset][armis_sdk.entities.asset.Asset].

        Yields:
            Field descriptions including field name, type, and other metadata.

        Example:
            ```python linenums="1" hl_lines="9"
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
        # pylint: disable=line-too-long
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

    @classmethod
    def _create_bulk_update_request(
        cls,
        asset: Asset,
        asset_id: Union[str, int],
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
    ) -> Union[str, int]:
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
                raise ArmisError(
                    f"Device at index {index} doesn't have exactly one mac address"
                )
            return device.mac_addresses[0]

        if asset_id_source == "IPV4_ADDRESS":
            if device.ipv4_addresses is None or len(device.ipv4_addresses) != 1:
                raise ArmisError(
                    f"Device at index {index} doesn't have exactly one IPv4 address"
                )
            return device.ipv4_addresses[0]

        if asset_id_source == "IPV6_ADDRESS":
            if device.ipv6_addresses is None or len(device.ipv6_addresses) != 1:
                raise ArmisError(
                    f"Device at index {index} doesn't have exactly one IPv6 address"
                )
            return device.ipv6_addresses[0]

        if asset_id_source == "SERIAL_NUMBER":
            if device.serial_numbers is None or len(device.serial_numbers) != 1:
                raise ArmisError(
                    f"Device at index {index} doesn't have exactly one serial number"
                )
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
        asset_class: Type[AssetT],
        fields: Optional[list[str]],
        filter_: dict,
    ) -> AsyncIterator[AssetT]:
        fields = fields or sorted(asset_class.all_fields())

        self._validate_fields(asset_class, fields)

        body = {
            "asset_type": asset_class.asset_type,
            "fields": fields,
            "filter": filter_,
        }
        async for item in self._armis_client.list("/v3/assets/_search", body=body):
            yield asset_class.from_search_result(item)

    @classmethod
    def _validate_asset_class(cls, assets: list[AssetT]):
        asset_types = {type(asset) for asset in assets}
        if len(asset_types) > 1:
            asset_types_str = ", ".join(sorted(repr(at.__name__) for at in asset_types))
            raise ArmisError(
                "All assets must be of the same type, "
                f"got {len(asset_types)} types: {asset_types_str}"
            )

    @classmethod
    def _validate_fields(
        cls,
        asset_class: Type[AssetT],
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
            raise ArmisError(
                f"The following fields are not supported with this operation: {fields_str}"
            )
