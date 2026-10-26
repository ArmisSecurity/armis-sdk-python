import dataclasses


@dataclasses.dataclass
class ClientCredentials:
    audience: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    vendor_id: str | None = None
    scopes: list[str] | None = None
