import datetime

import pandas

from armis_sdk.entities.data_export.device_merge_event import DeviceMergeEvent


def test_series_to_model():
    series = pandas.Series({"original_device_id": 1, "merge_timestamp": 1762000000, "current_active_device_id": 2})

    assert DeviceMergeEvent.series_to_model(series) == DeviceMergeEvent(
        original_device_id=1,
        merge_timestamp=datetime.datetime(2025, 11, 1, 12, 26, 40, tzinfo=datetime.UTC),
        current_active_device_id=2,
    )


def test_series_to_model_empty():
    assert DeviceMergeEvent.series_to_model(pandas.Series()) == DeviceMergeEvent()
