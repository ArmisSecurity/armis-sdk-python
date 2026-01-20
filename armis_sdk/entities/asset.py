import collections
from typing import Any
from typing import ClassVar
from typing import DefaultDict
from typing import Literal
from typing import Type
from typing import TypeVar

from pydantic import Field

from armis_sdk.core.base_entity import BaseEntity

AssetT = TypeVar("AssetT", bound="Asset")


class Asset(BaseEntity):
    """
    A base class for all assets type to inherit from.
    """

    asset_type: ClassVar[Literal["DEVICE"]]
    custom: dict[str, Any] = Field(default_factory=dict)
    """Custom properties of the asset. Values can by anything."""

    integration: dict[str, Any] = Field(default_factory=dict)
    """Integration properties of the asset. Values can by anything."""

    @classmethod
    def from_search_result(cls: Type[AssetT], data: dict) -> AssetT:
        fields: DefaultDict[str, Any] = collections.defaultdict(dict)
        for key, value in data["fields"].items():
            if len(parts := key.split(".", 1)) > 1:
                part1, part2 = parts
                fields[part1][part2] = value
            else:
                fields[key] = value

        return cls(**fields)

    @classmethod
    def all_fields(cls) -> set[str]:
        # Pylint doesn't recognize that "cls.model_fields" is a dict and not a method
        # so it's complaining that the method doesn't have a "keys" attribute.
        return set(cls.model_fields.keys()) - {
            "custom",
            "integration",
        }  # pylint: disable=no-member
