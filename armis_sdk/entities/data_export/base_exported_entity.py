import abc
from collections.abc import Iterable
from typing import Self
from typing import TypeVar

import pandas
from pydantic import BaseModel


T = TypeVar("T", bound="BaseExportedEntity")


class BaseExportedEntity(BaseModel, abc.ABC):
    @classmethod
    @abc.abstractmethod
    def series_to_model(cls, series: pandas.Series) -> Self: ...

    @property
    @abc.abstractmethod
    def entity_name(self): ...

    @classmethod
    def _to_list(cls, value) -> list | None:
        return [item for item in value if cls._value_or_none(item)] if isinstance(value, Iterable) else None

    @classmethod
    def _value_or_none(cls, value):
        if not value or pandas.isna(value) or value == "N/A":
            return None

        if isinstance(value, pandas.Timestamp):
            return value.to_pydatetime()

        return value
