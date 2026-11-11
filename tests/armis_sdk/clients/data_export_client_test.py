import datetime
from typing import ClassVar
from unittest import mock

import pandas
import pytest
import pytest_httpx

from armis_sdk.clients.data_export_client import DataExportClient
from armis_sdk.entities.data_export.base_exported_entity import BaseExportedEntity
from armis_sdk.entities.data_export.data_export import DataExport


pytest_plugins = ["tests.plugins.auto_setup_plugin"]


class MockEntity(BaseExportedEntity):
    entity_name: ClassVar[str] = "mock-entity"

    name: str
    description: str

    @classmethod
    def series_to_model(cls, series: pandas.Series) -> "MockEntity":
        return MockEntity(name=series.loc["name"], description=series.loc["description"])


async def test_disable(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/data-export/mock-entity",
        method="PATCH",
        match_json={"enabled": False},
    )

    data_export_client = DataExportClient()
    await data_export_client.disable(MockEntity)


async def test_enable(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/data-export/mock-entity",
        method="PATCH",
        match_json={"enabled": True},
    )

    data_export_client = DataExportClient()
    await data_export_client.enable(MockEntity)


@pytest.mark.parametrize("enabled", [True, False])
async def test_toggle(enabled: bool, httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/data-export/mock-entity",
        method="PATCH",
        match_json={"enabled": enabled},
    )

    data_export_client = DataExportClient()
    await data_export_client.toggle(MockEntity, enabled)


async def test_get(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/data-export/mock-entity",
        json={
            "enabled": True,
            "urls": ["url1", "url2"],
            "urls_creation_time": "2025-09-08T00:00:00",
            "file_format": "parquet",
        },
    )

    data_export_client = DataExportClient()
    result = await data_export_client.get(MockEntity)

    assert result == DataExport(
        enabled=True,
        urls=["url1", "url2"],
        urls_creation_time=datetime.datetime(2025, 9, 8, 0, 0),
        file_format="parquet",
    )


@mock.patch.object(pandas, "read_parquet")
async def test_iterate(mock_read_parquet: mock.MagicMock, httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/data-export/mock-entity",
        json={
            "enabled": True,
            "urls": ["url1", "url2"],
            "urls_creation_time": "2025-09-08T00:00:00",
            "file_format": "parquet",
        },
    )
    mock_read_parquet.side_effect = [
        pandas.DataFrame({"name": ["table", "chair"], "description": ["round", "high"]}),
        pandas.DataFrame({"name": ["book"], "description": ["hardcover"]}),
    ]

    data_export_client = DataExportClient()
    items = []
    async for item in data_export_client.iterate(MockEntity):
        items.append(item)

    assert items == [
        MockEntity(name="table", description="round"),
        MockEntity(name="chair", description="high"),
        MockEntity(name="book", description="hardcover"),
    ]

    mock_read_parquet.assert_has_calls(
        [
            mock.call("url1"),
            mock.call("url2"),
        ],
        any_order=False,
    )


async def test_enable_with_time_frame_days(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/data-export/mock-entity",
        method="PATCH",
        match_json={"enabled": True, "time_frame_days": 7},
    )

    await DataExportClient().enable(MockEntity, time_frame_days=7)


async def test_disable_with_time_frame_days(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/data-export/mock-entity",
        method="PATCH",
        match_json={"enabled": False, "time_frame_days": 7},
    )

    await DataExportClient().disable(MockEntity, time_frame_days=7)


async def test_get_with_time_frame_days(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/data-export/mock-entity?time_frame_days=7",
        json={
            "enabled": True,
            "urls": ["url1"],
            "urls_creation_time": "2025-09-08T00:00:00",
            "source_data_timestamp": "2025-09-07T00:00:00",
        },
    )

    result = await DataExportClient().get(MockEntity, time_frame_days=7)

    assert result.source_data_timestamp == datetime.datetime(2025, 9, 7)


@mock.patch.object(pandas, "read_parquet")
async def test_iterate_with_time_frame_days(mock_read_parquet: mock.MagicMock, httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/data-export/mock-entity?time_frame_days=7",
        json={"enabled": True, "urls": ["url1"], "urls_creation_time": "2025-09-08T00:00:00"},
    )
    mock_read_parquet.return_value = pandas.DataFrame([{"name": "a", "description": "b"}])

    rows = [row async for row in DataExportClient().iterate(MockEntity, time_frame_days=7)]

    assert rows == [MockEntity(name="a", description="b")]
