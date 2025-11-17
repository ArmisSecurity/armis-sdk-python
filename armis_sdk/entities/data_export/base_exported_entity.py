import abc
from typing import Type
from typing import TypeVar

import pandas
from pydantic import BaseModel

T = TypeVar("T", bound="BaseExportedEntity")


class BaseExportedEntity(BaseModel, abc.ABC):
    @classmethod
    @abc.abstractmethod
    def series_to_model(cls: Type[T], series: pandas.Series) -> T: ...

    @property
    @abc.abstractmethod
    def entity_name(self): ...

    @classmethod
    def _to_list(cls, value) -> list:
        return [item for item in value if cls._value_or_none(item)]

    @classmethod
    def _value_or_none(cls, value):
        if not value or pandas.isnull(value) or value == "N/A":
            return None

        if isinstance(value, pandas.Timestamp):
            return value.to_pydatetime()

        return value
