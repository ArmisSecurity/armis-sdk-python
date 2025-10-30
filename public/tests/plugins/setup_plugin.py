import datetime

import pytest
import pytest_httpx


@pytest.fixture
def setup_env_variables(monkeypatch):
    monkeypatch.setenv("ARMIS_AUDIENCE", "https://mock.armis.com/")
    monkeypatch.setenv("ARMIS_CLIENT_ID", "mock_client_id")
    monkeypatch.setenv("ARMIS_CLIENT_SECRET", "mock_client_secret")
    monkeypatch.setenv("ARMIS_SCOPES", "ALL")
    monkeypatch.setenv("ARMIS_VENDOR_ID", "mock_vendor_id")


@pytest.fixture
def authorized(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/oauth/token",
        method="POST",
        match_json={
            "grant_type": "client_credentials",
            "vendor_id": "mock_vendor_id",
            "audience": "https://mock.armis.com/",
            "client_id": "mock_client_id",
            "client_secret": "mock_client_secret",
            "scopes": ["ALL"],
        },
        json={
            "access_token": "mock_access_token",
            "token_type": "Bearer",
            "expires_in": datetime.timedelta(minutes=1).total_seconds(),
        },
    )
