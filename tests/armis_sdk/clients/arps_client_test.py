import datetime
import io

import pytest_httpx

from armis_sdk.clients.arps_client import ArpsClient
from armis_sdk.entities.arp_upload_result import ArpUploadResult


pytest_plugins = ["tests.plugins.auto_setup_plugin"]


async def test_upload_file_object(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/arps",
        method="POST",
        match_data={"expiration": "2026-12-31T00:00:00+00:00", "network_id": "net1"},
        match_files={"file": ("arps.csv", b"ip,mac\n1.1.1.1,aa\n", "text/csv")},
        json={
            "total_rows": 2,
            "accepted_records": 1,
            "duplicate_rows": 1,
            "expiration": "2026-12-31T00:00:00Z",
        },
        status_code=202,
    )

    result = await ArpsClient().upload(
        io.BytesIO(b"ip,mac\n1.1.1.1,aa\n"),
        datetime.datetime(2026, 12, 31, tzinfo=datetime.UTC),
        "net1",
    )

    assert result == ArpUploadResult(
        total_rows=2,
        accepted_records=1,
        duplicate_rows=1,
        expiration=datetime.datetime(2026, 12, 31, tzinfo=datetime.UTC),
    )


async def test_upload_path(httpx_mock: pytest_httpx.HTTPXMock, tmp_path):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/arps",
        method="POST",
        json={
            "total_rows": 2,
            "accepted_records": 1,
            "duplicate_rows": 1,
            "expiration": "2026-12-31T00:00:00Z",
        },
        status_code=202,
    )
    path = tmp_path / "arps.csv"
    path.write_text("ip,mac\n1.1.1.1,aa\n")

    result = await ArpsClient().upload(
        str(path),
        datetime.datetime(2026, 12, 31, tzinfo=datetime.UTC),
        "net1",
    )

    assert result == ArpUploadResult(
        total_rows=2,
        accepted_records=1,
        duplicate_rows=1,
        expiration=datetime.datetime(2026, 12, 31, tzinfo=datetime.UTC),
    )
