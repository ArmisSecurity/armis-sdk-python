import dataclasses
from typing import Optional


@dataclasses.dataclass
class ClientCredentials:
    audience: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    vendor_id: Optional[str] = None
    scopes: Optional[list[str]] = None
