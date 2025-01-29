from json import JSONDecodeError
from typing import Optional
from typing import Union

import httpx
from httpx import HTTPStatusError

from armis_sdk.core.armis_error import AlreadyExistsError
from armis_sdk.core.armis_error import BadRequestError
from armis_sdk.core.armis_error import NotFoundError
from armis_sdk.core.armis_error import ResponseError


def parse_response(response: httpx.Response) -> Optional[Union[dict, list]]:
    try:
        return response.json()
    except JSONDecodeError as error:
        message = f"Response body is not a valid JSON: {response.text}"
        raise ResponseError(message) from error


def raise_for_status(response: httpx.Response):
    try:
        response.raise_for_status()
    except HTTPStatusError as error:
        parsed = parse_response(error.response)
        message = parsed.get("message", "Something went wrong.")

        if error.response.status_code == httpx.codes.NOT_FOUND:
            raise NotFoundError(message, response_errors=[error]) from error

        if error.response.status_code == httpx.codes.BAD_REQUEST:
            raise BadRequestError(message, response_errors=[error]) from error

        if error.response.status_code == httpx.codes.CONFLICT:
            raise AlreadyExistsError(message, response_errors=[error]) from error

        raise ResponseError(message, response_errors=[error]) from error
