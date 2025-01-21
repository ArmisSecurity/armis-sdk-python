from typing import List

from httpx import HTTPStatusError


class ArmisError(Exception):
    pass


class ResponseError(ArmisError):
    def __init__(self, *args, response_errors: List[HTTPStatusError] = None):
        super().__init__(*args)
        self.response_errors = response_errors
