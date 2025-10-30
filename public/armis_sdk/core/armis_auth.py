import datetime
import typing
from typing import Optional

import httpx

from armis_sdk.core import response_utils
from armis_sdk.core.armis_error import ArmisError
from armis_sdk.core.client_credentials import ClientCredentials

AUTHORIZATION = "Authorization"


class ArmisAuth(httpx.Auth):
    """
    This class takes care of authentication for the Armis API.
    The general flow is as follows:

    1. Before performing any request check if there's a valid access token.
    2. If there is, use it with the `Authorization` header.
    3. If there isn't, make a POST request to `/v3/oauth/token`
       to generate a new access token.
    4. Save the new access token and also use it with the `Authorization` header.
    """

    requires_response_body = True

    def __init__(self, base_url: str, credentials: ClientCredentials):
        self._base_url = base_url
        self._credentials = credentials
        self._access_token: Optional[str] = None
        self._expires_at: Optional[datetime.datetime] = None

    def auth_flow(
        self, request: httpx.Request
    ) -> typing.Generator[httpx.Request, httpx.Response, None]:
        if (
            self._access_token is None
            or self._expires_at is None
            or self._expires_at < datetime.datetime.now()
        ):
            access_token_response = yield self._build_access_token_request()
            self._update_access_token(access_token_response)

        if self._access_token is None:
            raise ArmisError(
                "Something went wrong, there is no access token available."
            )

        request.headers[AUTHORIZATION] = f"Bearer {self._access_token}"
        response = yield request

        if response.status_code == httpx.codes.UNAUTHORIZED:
            access_token_response = yield self._build_access_token_request()
            self._update_access_token(access_token_response)

            request.headers[AUTHORIZATION] = f"Bearer {self._access_token}"
            yield request

    def _build_access_token_request(self):
        return httpx.Request(
            "POST",
            f"{self._base_url}/v3/oauth/token",
            json={
                "grant_type": "client_credentials",
                "vendor_id": self._credentials.vendor_id,
                "audience": self._credentials.audience,
                "client_id": self._credentials.client_id,
                "client_secret": self._credentials.client_secret,
                "scopes": self._credentials.scopes,
            },
        )

    def _update_access_token(self, response: httpx.Response):
        data = response_utils.get_data_dict(response)
        self._access_token = data["access_token"]
        self._expires_at = datetime.datetime.now() + datetime.timedelta(
            seconds=data["expires_in"]
        )
