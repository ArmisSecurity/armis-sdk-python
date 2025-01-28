import importlib.metadata
import os
from typing import Optional

import httpx

from armis_sdk.core.armis_auth import ArmisAuth

ARMIS_PAGE_SIZE = "ARMIS_PAGE_SIZE"
ARMIS_SECRET_KEY = "ARMIS_SECRET_KEY"
ARMIS_TENANT = "ARMIS_TENANT"
ARMIS_CLIENT_ID = "ARMIS_CLIENT_ID"
BASE_URL = "https://{tenant}.armis.com"
DEFAULT_PAGE_LENGTH = 100
VERSION = importlib.metadata.version("armis_sdk")


class ArmisClient:  # pylint: disable=too-few-public-methods
    """
    A class that provides easy access to the Armis API, taking care of authenticating requests.
    """

    def __init__(
        self,
        tenant: Optional[str] = None,
        secret_key: Optional[str] = None,
        client_id: Optional[str] = None,
    ):
        tenant = os.getenv(ARMIS_TENANT, tenant)
        secret_key = os.getenv(ARMIS_SECRET_KEY, secret_key)
        client_id = os.getenv(ARMIS_CLIENT_ID, client_id)

        if not tenant:
            raise ValueError(
                f"Either populate the {ARMIS_TENANT!r} environment variable "
                f"or pass an explicit value to the constructor"
            )
        if not secret_key:
            raise ValueError(
                f"Either populate the {ARMIS_SECRET_KEY!r} environment variable "
                f"or pass an explicit value to the constructor"
            )
        if not client_id:
            raise ValueError(
                f"Either populate the {ARMIS_CLIENT_ID!r} environment variable "
                f"or pass an explicit value to the constructor"
            )

        self._base_url = BASE_URL.format(tenant=tenant)
        self._auth = ArmisAuth(self._base_url, secret_key)
        self._user_agent = f"ArmisPythonSDK/v{VERSION}"
        self._client_id = client_id

    def client(self):
        return httpx.AsyncClient(
            auth=self._auth,
            base_url=self._base_url,
            headers={
                "User-Agent": self._user_agent,
                "Armis-API-Client-Id": self._client_id,
            },
        )
