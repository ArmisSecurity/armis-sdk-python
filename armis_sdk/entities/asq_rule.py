from typing import List
from typing import Optional
from typing import Union

from pydantic import Field
from pydantic import model_validator

from armis_sdk.core.base_entity import BaseEntity


class AsqRule(BaseEntity):
    """
    A class representing an ASQ Rule.
    An ASQ rule consist of a set of conditions with either "and" or "or"
    relationship between them.
    Each item in a set of rules can be a string or a (nested) instance of `AsqRule`.

    Examples:
        A simple rule that only matches `asq1`.
        ```python
        AsqRule(and_=["asq1"])
        # or
        AsqRule(or_=["asq1"])
        # or
        AsqRule.from_asq("asq1")
        ```

        A rule that matches either `asq1` _or_ `asq2` (or both).
        ```python
        AsqRule(or_=["asq1", "asq2"])
        ```

        A rule that matches both `asq1` _and_ `asq2`.
        ```python
        AsqRule(and_=["asq1", "asq2"])
        ```

        A rule that matches `asq1` _and_ either `asq2` _or_ `asq3` (or both).
        ```python
        AsqRule(and_=["asq1", AsqRule(or_=["asq2", "asq3"])])
        ```
    """

    and_: Optional[List[Union[str, "AsqRule"]]] = Field(alias="and", default=None)
    """Rules that all must match."""

    or_: Optional[List[Union[str, "AsqRule"]]] = Field(alias="or", default=None)
    """Rules that at least one of them must match."""

    @classmethod
    def from_asq(cls, asq: str) -> "AsqRule":
        """
        Create a `AsqRule` object from a single ASQ string.
        """
        return AsqRule(or_=[asq])

    @model_validator(mode="after")
    def validate_structure(self) -> "AsqRule":
        if (self.and_ is None) == (self.or_ is None):
            raise ValueError("Only one of 'and_' or 'or_' must be specified.")

        return self
