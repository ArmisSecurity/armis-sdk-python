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


async def test_retries(monkeypatch, httpx_mock: pytest_httpx.HTTPXMock):
    monkeypatch.setenv("ARMIS_REQUEST_RETRIES", "2")
    monkeypatch.setenv("ARMIS_REQUEST_BACKOFF", "0")
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/mock/endpoint",
        status_code=httpx.codes.GATEWAY_TIMEOUT,  # original request, fails
    )
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/mock/endpoint",
        status_code=httpx.codes.GATEWAY_TIMEOUT,  # first retry, fails again
    )
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/mock/endpoint",
        status_code=httpx.codes.OK,  # second retry, succeeds
    )

    armis_client = ArmisClient()
    async with armis_client.client() as client:
        response = await client.get("/mock/endpoint")

    assert response.status_code == httpx.codes.OK


async def test_retries_with_eventual_failure(
    monkeypatch, httpx_mock: pytest_httpx.HTTPXMock
):
    monkeypatch.setenv("ARMIS_REQUEST_RETRIES", "2")
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/mock/endpoint",
        status_code=httpx.codes.GATEWAY_TIMEOUT,  # original request, fails
    )
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/mock/endpoint",
        status_code=httpx.codes.GATEWAY_TIMEOUT,  # first retry, fails again
    )
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/mock/endpoint",
        status_code=httpx.codes.GATEWAY_TIMEOUT,  # second retry, fails again
    )

    armis_client = ArmisClient()
    async with armis_client.client() as client:
        response = await client.get("/mock/endpoint")

    assert response.status_code == httpx.codes.GATEWAY_TIMEOUT


async def test_retrie_with_writable_method(
    monkeypatch, httpx_mock: pytest_httpx.HTTPXMock
):
    monkeypatch.setenv("ARMIS_REQUEST_RETRIES", "2")
    httpx_mock.add_response(
        method="POST",
        url="https://mock_tenant.armis.com/mock/endpoint",
        status_code=httpx.codes.GATEWAY_TIMEOUT,  # original request, fails - shouldn't retry!
    )

    armis_client = ArmisClient()
    async with armis_client.client() as client:
        response = await client.post("/mock/endpoint")

    assert response.status_code == httpx.codes.GATEWAY_TIMEOUT


async def test_list_with_multiple_pages(
    monkeypatch, httpx_mock: pytest_httpx.HTTPXMock
):
    monkeypatch.setenv("ARMIS_PAGE_SIZE", "2")
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/?from=0&length=2",
        method="GET",
        json={
            "data": {
                "next": 2,
                "sites": [
                    {"id": "1", "name": "mock_site_1"},
                    {"id": "2", "name": "mock_site_2"},
                ],
            }
        },
    )
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/?from=2&length=2",
        method="GET",
        json={
            "data": {
                "next": 4,
                "sites": [
                    {"id": "3", "name": "mock_site_3"},
                    {"id": "4", "name": "mock_site_4"},
                ],
            }
        },
    )
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/sites/?from=4&length=2",
        method="GET",
        json={
            "data": {
                "next": None,
                "sites": [
                    {"id": "5", "name": "mock_site_5"},
                ],
            }
        },
    )

    armis_client = ArmisClient()
    items = [item async for item in armis_client.list("/api/v1/sites/", "sites")]

    assert items == [
        {"id": "1", "name": "mock_site_1"},
        {"id": "2", "name": "mock_site_2"},
        {"id": "3", "name": "mock_site_3"},
        {"id": "4", "name": "mock_site_4"},
        {"id": "5", "name": "mock_site_5"},
    ]


async def test_proxy_configuration(monkeypatch, httpx_mock: pytest_httpx.HTTPXMock):
    """Test that proxy environment variables are properly configured in the client."""
    
    proxy_url = "http://test-proxy:8080"
    monkeypatch.setenv("HTTPS_PROXY", proxy_url)
    
    httpx_mock.add_response(
        method="POST",
        url="https://mock_tenant.armis.com/api/v1/access_token/",
        json={
            "data": {
                "access_token": "mock_token",
                "expires_in": 3600
            }
        }
    )
    
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/mock/endpoint",
        json={"success": True}
    )

    armis_client = ArmisClient()
    
    proxy = armis_client._get_proxy_config()
    assert proxy == proxy_url, f"Expected {proxy_url}, got {proxy}"
    
    async with armis_client.client() as client:
        assert client._trust_env is True, "trust_env should be True for environment variable support"        
        
        # Test that requests work with proxy configuration
        response = await client.get("/mock/endpoint")
        assert response.status_code == 200
        assert response.json() == {"success": True}


async def test_proxy_environment_variable_priority(monkeypatch):
    """Test that proxy environment variables are checked in correct priority order."""
    
    monkeypatch.setenv("HTTP_PROXY", "http://lower-priority:8080")
    monkeypatch.setenv("HTTPS_PROXY", "http://higher-priority:8080")
    monkeypatch.setenv("http_proxy", "http://lowercase-priority:8080")

    armis_client = ArmisClient()
    
    proxy = armis_client._get_proxy_config()
    assert proxy == "http://higher-priority:8080", "HTTPS_PROXY should take priority"


async def test_proxy_with_authentication(monkeypatch):
    """Test proxy configuration with username and password."""
    
    proxy_url = "http://user:pass@proxy.company.com:8080"
    monkeypatch.setenv("HTTPS_PROXY", proxy_url)

    armis_client = ArmisClient()
    
    proxy = armis_client._get_proxy_config()
    assert proxy == proxy_url, "Proxy with auth should be configured correctly"