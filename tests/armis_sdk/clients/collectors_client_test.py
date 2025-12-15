import datetime
import tempfile

import pytest_httpx

from armis_sdk.clients.collectors_client import CollectorsClient
from armis_sdk.entities.collector_image import CollectorImage
from armis_sdk.entities.download_progress import DownloadProgress
from armis_sdk.enums.collector_image_type import CollectorImageType

pytest_plugins = ["tests.plugins.auto_setup_plugin"]


async def test_get_image(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/collectors/_image?image_type=OVA",
        json={
            "image_type": "OVA",
            "image_password": "test_password",
            "url": "https://example.com/collector.ova",
            "url_expiration_date": "2025-12-10T00:00:00",
        },
    )

    collectors_client = CollectorsClient()
    collector_image = await collectors_client.get_image()

    assert collector_image == CollectorImage(
        image_type=CollectorImageType.OVA,
        image_password="test_password",
        url="https://example.com/collector.ova",
        url_expiration_date=datetime.datetime(2025, 12, 10),
    )


async def test_get_with_explicit_image_type(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/collectors/_image?image_type=QCOW2",
        json={
            "image_type": "QCOW2",
            "image_password": "test_password_qcow2",
            "url": "https://example.com/collector.qcow2",
            "url_expiration_date": "2025-12-11T00:00:00",
        },
    )

    collectors_client = CollectorsClient()
    collector_image = await collectors_client.get_image(
        image_type=CollectorImageType.QCOW2
    )

    assert collector_image == CollectorImage(
        image_type=CollectorImageType.QCOW2,
        image_password="test_password_qcow2",
        url="https://example.com/collector.qcow2",
        url_expiration_date=datetime.datetime(2025, 12, 11),
    )


async def test_download_image_to_path(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/collectors/_image?image_type=OVA",
        json={
            "image_type": "OVA",
            "image_password": "test_password",
            "url": "https://example.com/collector.ova",
            "url_expiration_date": "2025-12-10T00:00:00",
        },
    )
    httpx_mock.add_response(
        url="https://example.com/collector.ova",
        stream=pytest_httpx.IteratorStream([b"a" * 16384, b"b" * 16384, b"c" * 16383]),
        headers={"Content-Length": "49151"},
    )

    collectors_client = CollectorsClient()
    with tempfile.NamedTemporaryFile() as temp_file:
        progress_items = [
            site async for site in collectors_client.download_image(temp_file.name)
        ]

        assert progress_items == [
            DownloadProgress(downloaded=16384, total=49151),
            DownloadProgress(downloaded=32768, total=49151),
            DownloadProgress(downloaded=49151, total=49151),
        ]

        assert temp_file.read() == b"a" * 16384 + b"b" * 16384 + b"c" * 16383


async def test_download_image_to_file(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/collectors/_image?image_type=OVA",
        json={
            "image_type": "OVA",
            "image_password": "test_password",
            "url": "https://example.com/collector.ova",
            "url_expiration_date": "2025-12-10T00:00:00",
        },
    )
    httpx_mock.add_response(
        url="https://example.com/collector.ova",
        stream=pytest_httpx.IteratorStream([b"a" * 16384, b"b" * 16384, b"c" * 16383]),
        headers={"Content-Length": "49151"},
    )

    collectors_client = CollectorsClient()
    with tempfile.NamedTemporaryFile() as temp_file:
        progress_items = [
            site async for site in collectors_client.download_image(temp_file)
        ]

        assert progress_items == [
            DownloadProgress(downloaded=16384, total=49151),
            DownloadProgress(downloaded=32768, total=49151),
            DownloadProgress(downloaded=49151, total=49151),
        ]
        temp_file.seek(0)
        assert temp_file.read() == b"a" * 16384 + b"b" * 16384 + b"c" * 16383
