import datetime
import json

import pandas

from armis_sdk.entities.data_export.risk_factor import RiskFactor
from armis_sdk.entities.data_export.risk_factor import RiskFactorRecommendedAction


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
            "remediation": "remediation1",
            "remediation_description": "remediation_description1",
            "remediation_recommended_actions": json.dumps(
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


def test_series_to_model_empty():
    series = pandas.Series()

    assert RiskFactor.series_to_model(series) == RiskFactor(
        device_id=None,
        category=None,
        type=None,
        description=None,
        score=None,
        status=None,
        group=None,
        remediation_type=None,
        remediation_description=None,
        remediation_recommended_actions=None,
        first_seen=None,
        last_seen=None,
        status_update_time=None,
        status_updated_by_user_id=None,
        status_update_reason=None,
    )
