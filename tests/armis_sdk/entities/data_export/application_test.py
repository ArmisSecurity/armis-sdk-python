import collections
import datetime

import pandas

from armis_sdk.entities.data_export.application import Application

ApplicationNT = collections.namedtuple(
    "ApplicationNT",
    ["device_id", "name", "vendor", "version", "cpe", "first_seen", "last_seen"],
)


def test_series_to_model():
    series = pandas.Series(
        {
            "device_id": 1,
            "name": "Chrome",
            "vendor": "Google",
            "version": "1.2.3",
            "cpe": "cpe1",
            "first_seen": pandas.Timestamp.fromisoformat("2025-11-01"),
            "last_seen": pandas.Timestamp.fromisoformat("2025-11-04"),
        },
    )

    assert Application.series_to_model(series) == Application(
        device_id=1,
        vendor="Google",
        name="Chrome",
        version="1.2.3",
        cpe="cpe1",
        first_seen=datetime.datetime(2025, 11, 1),
        last_seen=datetime.datetime(2025, 11, 4),
    )
