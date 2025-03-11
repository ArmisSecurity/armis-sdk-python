import importlib.metadata
import platform
import httpx
import pytest_httpx

from armis_sdk.core.armis_client import ArmisClient

pytest_plugins = ["tests.plugins.auto_setup_plugin"]

try:
    VERSION = importlib.metadata.version("armis_sdk")
except importlib.metadata.PackageNotFoundError:
    VERSION = "unknown"


async def test_request_headers(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        match_headers={
            "User-Agent": (
                f"Python/{platform.python_version()} "
                f"python-httpx/{httpx.__version__} "
                f"ArmisPythonSDK/v{VERSION}"
            ),
            "Armis-API-Client-Id": "mock_client_id",
        },
        url="https://mock_tenant.armis.com/mock/endpoint",
    )

    armis_client = ArmisClient()
    async with armis_client.client() as client:
        await client.get("/mock/endpoint")
