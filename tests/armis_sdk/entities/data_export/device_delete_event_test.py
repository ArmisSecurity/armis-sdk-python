import datetime

import pandas

from armis_sdk.entities.data_export.device_delete_event import DeviceDeleteEvent


def test_series_to_model():
    series = pandas.Series({"device_id": 1, "deleted_timestamp": 1762000000})

    assert DeviceDeleteEvent.series_to_model(series) == DeviceDeleteEvent(
        device_id=1,
        deleted_timestamp=datetime.datetime(2025, 11, 1, 12, 26, 40, tzinfo=datetime.UTC),
    )


def test_series_to_model_empty():
    assert DeviceDeleteEvent.series_to_model(pandas.Series()) == DeviceDeleteEvent()
