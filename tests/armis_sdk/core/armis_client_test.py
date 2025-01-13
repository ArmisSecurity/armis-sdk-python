import importlib.metadata

import pytest_httpx

from armis_sdk.core.armis_client import ArmisClient

pytest_plugins = ["tests.plugins.setup_plugin"]

VERSION = importlib.metadata.version("armis_sdk")


async def test_request_headers(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        match_headers={
            "User-Agent": f"ArmisPythonSDK/v{VERSION}",
            "Armis-API-Client-Id": "mock_client_id",
        },
        url="https://mock_tenant.armis.com/mock/endpoint",
    )

    armis_client = ArmisClient()
    async with armis_client.client() as client:
        await client.get("/mock/endpoint")
