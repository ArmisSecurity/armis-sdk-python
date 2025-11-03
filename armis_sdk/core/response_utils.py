import json
from json import JSONDecodeError
from typing import Type
from typing import TypeVar

import httpx
from httpx import HTTPStatusError
from pydantic import ValidationError

from armis_sdk.core.armis_error import AlreadyExistsError
from armis_sdk.core.armis_error import BadRequestError
from armis_sdk.core.armis_error import ErrorBody
from armis_sdk.core.armis_error import NotFoundError
from armis_sdk.core.armis_error import ResponseError

DataTypeT = TypeVar("DataTypeT", dict, list)


def get_data(
    response: httpx.Response,
    data_type: Type[DataTypeT],
) -> DataTypeT:
    raise_for_status(response)
    data = parse_response(response, dict)

    if not isinstance(data, data_type):
        detail = "Response data represents neither a dict nor a list."
        raise ResponseError(ErrorBody(detail=detail))

    return data


def get_data_dict(response: httpx.Response):
    return get_data(response, dict)


def parse_response(
    response: httpx.Response,
    data_type: Type[DataTypeT],
) -> DataTypeT:
    try:
        response_data = response.json()
    except JSONDecodeError as error:
        detail = f"Response body is not a valid JSON: {response.text}"
        raise ResponseError(ErrorBody(detail=detail)) from error

    if not isinstance(response_data, data_type):
        detail = "Response body represents neither a dict nor a list."
        raise ResponseError(ErrorBody(detail=detail))

    return response_data


def raise_for_status(response: httpx.Response):
    try:
        response.raise_for_status()
    except HTTPStatusError as error:
        parsed = parse_response(error.response, dict)
        try:
            error_body = ErrorBody.model_validate(parsed)
        except ValidationError:
            error_body = ErrorBody(detail=json.dumps(parsed))

        if error.response.status_code == httpx.codes.NOT_FOUND:
            raise NotFoundError(error_body, response_errors=[error]) from error

        if error.response.status_code == httpx.codes.BAD_REQUEST:
            raise BadRequestError(error_body, response_errors=[error]) from error

        if error.response.status_code == httpx.codes.CONFLICT:
            raise AlreadyExistsError(error_body, response_errors=[error]) from error

        raise ResponseError(error_body, response_errors=[error]) from error
