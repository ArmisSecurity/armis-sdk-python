from armis_sdk.core.base_entity import BaseEntity


class Boundary(BaseEntity):
    """A `Boundary` is a logical segment in the network."""

    id: int
    """The id of the boundary."""

    name: str
    """The name of the boundary."""
