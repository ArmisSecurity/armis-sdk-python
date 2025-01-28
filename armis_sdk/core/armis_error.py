"""
This module contains the various classes of errors that you may encounter
while interacting with the SDK.
"""

from typing import List

from httpx import HTTPStatusError


class ArmisError(Exception):
    """
    A base class for all errors raised by this SDK.
    """


class ResponseError(ArmisError):
    # pylint: disable=line-too-long
    """
    A class for all errors raised following a non-successful response from the Armis API.
    For example, if the server returns 400 for invalid input, an instance of this class will be raised.
    """

    def __init__(self, *args, response_errors: List[HTTPStatusError] = None):
        super().__init__(*args)
        self.response_errors = response_errors
