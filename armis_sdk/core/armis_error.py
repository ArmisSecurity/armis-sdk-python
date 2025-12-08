"""
This module contains the various classes of errors that you may encounter
while interacting with the SDK.
"""

import json
from typing import List
from typing import Optional
from typing import Union

from httpx import HTTPStatusError
from pydantic import BaseModel


class DetailItem(BaseModel):
    loc: list[Union[str, int]]
    msg: str
    type: str

    def __str__(self):
        return (
            f"Type: {self.type}\n"
            f"Message: {self.msg}\n"
            f"Location: {json.dumps(self.loc)}"
        )


class ErrorBody(BaseModel):
    detail: Union[str, List[DetailItem]]


class ArmisError(Exception):
    """
    A base class for all errors raised by this SDK.
    """


class BulkUpdateItemError(BaseModel):
    index: int
    request: dict
    response: dict


class BulkUpdateError(ArmisError):
    def __init__(self, items: list[BulkUpdateItemError]):
        self.items = items
        display = "\n".join(
            f"Failed to update item at index {item.index}. "
            f"Request: {json.dumps(item.request)}, "
            f"Response: {json.dumps(item.response)}"
            for item in items
        )
        super().__init__(display)


class ResponseError(ArmisError):
    # pylint: disable=line-too-long
    """
    A class for all errors raised following a non-successful response from the Armis API.
    For example, if the server returns 400 for invalid input, an instance of this class will be raised.
    """

    def __init__(
        self,
        error_body: ErrorBody,
        response_errors: Optional[List[HTTPStatusError]] = None,
    ):
        super().__init__(self._get_message(error_body))
        self.response_errors = response_errors
        self.detail = error_body.detail

    @classmethod
    def _get_message(cls, error_body: ErrorBody) -> str:
        if isinstance(error_body.detail, str):
            return error_body.detail

        return "\n\n".join(str(item) for item in error_body.detail)


class AlreadyExistsError(ResponseError):
    """
    A class for all errors raised when an attempt is made to create a resource that already exists.
    """


class BadRequestError(ResponseError):
    """
    A class for all errors raised when a requested resource was malformed.
    """


class NotFoundError(ResponseError):
    """
    A class for all errors raised when a requested resource was not found.
    """
