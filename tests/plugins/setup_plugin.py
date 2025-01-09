import datetime

import pytest
import pytest_httpx


@pytest.fixture(autouse=True)
def setup_env_variables(monkeypatch):
    monkeypatch.setenv("ARMIS_CLIENT_ID", "mock_client_id")
    monkeypatch.setenv("ARMIS_SECRET_KEY", "mock_secret_key")
    monkeypatch.setenv("ARMIS_TENANT", "mock_tenant")


@pytest.fixture(autouse=True)
def authorized(httpx_mock: pytest_httpx.HTTPXMock):
    expire_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=1
    )
    httpx_mock.add_response(
        url="https://mock_tenant.armis.com/api/v1/access_token/",
        method="POST",
        json={
            "data": {
                "access_token": "mock_access_token",
                "expiration_utc": expire_at.isoformat(),
            }
        },
    )
