import datetime
import typing
from typing import Optional

import httpx

from armis_sdk.core import response_utils
from armis_sdk.core.armis_error import ArmisError

AUTHORIZATION = "Authorization"


class ArmisAuth(httpx.Auth):
    """
    This class takes care of authentication for the Armis API.
    The general flow is as follows:

    1. Before performing any request check if there's a valid access token.
    2. If there is, use it with the `Authorization` header.
    3. If there isn't, make a POST request to `/api/v1/access_token/`
       to generate a new access token.
    4. Save the new access token and also use it with the `Authorization` header.
    """

    requires_response_body = True

    def __init__(self, base_url: str, secret_key: str):
        self._base_url = base_url
        self._secret_key = secret_key
        self._access_token: Optional[str] = None
        self._expires_at: Optional[datetime.datetime] = None

    def auth_flow(
        self, request: httpx.Request
    ) -> typing.Generator[httpx.Request, httpx.Response, None]:
        if (
            self._access_token is None
            or self._expires_at is None
            or self._expires_at < datetime.datetime.now(datetime.timezone.utc)
        ):
            access_token_response = yield self._build_access_token_request()
            self._update_access_token(access_token_response)

        if self._access_token is None:
            raise ArmisError(
                "Something went wrong, there is no access token available."
            )

        request.headers[AUTHORIZATION] = self._access_token
        response = yield request

        if response.status_code == httpx.codes.UNAUTHORIZED:
            access_token_response = yield self._build_access_token_request()
            self._update_access_token(access_token_response)

            request.headers[AUTHORIZATION] = self._access_token
            yield request

    def _build_access_token_request(self):
        return httpx.Request(
            "POST",
            f"{self._base_url}/api/v1/access_token/",
            json={"secret_key": self._secret_key},
        )

    def _update_access_token(self, response: httpx.Response):
        data = response_utils.get_data_dict(response)
        self._access_token = data["access_token"]
        self._expires_at = datetime.datetime.fromisoformat(data["expiration_utc"])
