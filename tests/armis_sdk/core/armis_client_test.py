import importlib.metadata
import platform

import httpx
import pytest
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


@pytest.mark.parametrize(
    ["env_var", "proxy_url", "expected_proxy"],
    [
        (
            "HTTP_PROXY",
            "http://test-proxy:8080?b=1&a=2",
            "http://test-proxy:8080/?a=2&b=1",
        ),
        (
            "HTTPS_PROXY",
            "https://user:pass@proxy.company.com:8080?b=1&a=2&c=3",
            "https://user:pass@proxy.company.com:8080/?c=3&b=1&a=2",
        ),
    ],
)
async def test_proxy(monkeypatch, httpx_mock, env_var, proxy_url, expected_proxy):
    monkeypatch.setenv(env_var, proxy_url)

    # proxy_url must match,
    # Order of parameters in the query string does not matter
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/mock/endpoint",
        proxy_url=expected_proxy,
        json={"ok": True},
    )

    async with ArmisClient().client() as client:
        resp = await client.get("/mock/endpoint")
        assert resp.json() == {"ok": True}
