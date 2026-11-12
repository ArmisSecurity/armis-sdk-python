import dataclasses


@dataclasses.dataclass
class ClientCredentials:
    """
    The values needed to authenticate against the Armis API.
    Any value left empty is read from the matching `ARMIS_*` environment variable.
    """

    audience: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    vendor_id: str | None = None
    scopes: list[str] | None = None
