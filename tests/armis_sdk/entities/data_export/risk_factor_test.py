import collections
import datetime
import json

import pandas

from armis_sdk.entities.data_export.risk_factor import RiskFactor
from armis_sdk.entities.data_export.risk_factor import RiskFactorRecommendedAction

RiskFactorNT = collections.namedtuple(
    "RiskFactorNT",
    [
        "device_id",
        "category",
        "type",
        "description",
        "score",
        "status",
        "group",
        "remidiation",
        "remidiation_description",
        "remoidiation_recommended_actions",
        "first_seen",
        "last_seen",
        "status_update_time",
        "status_updated_by_user_id",
        "status_update_reason",
    ],
)


def test_series_to_model():
    series = pandas.Series(
        {
            "device_id": 1,
            "category": "category1",
            "type": "type1",
            "description": "description1",
            "score": 2,
            "status": "OPEN",
            "group": "group1",
            "remidiation": "remediation1",
            "remidiation_description": "remediation_description1",
            "remoidiation_recommended_actions": json.dumps(
                [
                    {
                        "id": 1,
                        "title": "title1",
                        "description": "description1",
                        "type": "type1",
                    }
                ],
            ),
            "first_seen": pandas.Timestamp.fromisoformat("2025-11-01"),
            "last_seen": pandas.Timestamp.fromisoformat("2025-11-04"),
            "status_update_time": pandas.Timestamp.fromisoformat("2025-11-03"),
            "status_updated_by_user_id": 3,
            "status_update_reason": "reason1",
        },
    )

    assert RiskFactor.series_to_model(series) == RiskFactor(
        device_id=1,
        category="category1",
        type="type1",
        description="description1",
        score=2,
        status="OPEN",
        group="group1",
        remediation_type="remediation1",
        remediation_description="remediation_description1",
        remediation_recommended_actions=[
            RiskFactorRecommendedAction(
                id=1,
                title="title1",
                description="description1",
                type="type1",
            ),
        ],
        first_seen=datetime.datetime(2025, 11, 1),
        last_seen=datetime.datetime(2025, 11, 4),
        status_update_time=datetime.datetime(2025, 11, 3),
        status_updated_by_user_id=3,
        status_update_reason="reason1",
    )
