import pytest_httpx

from armis_sdk.clients.policies_client import PoliciesClient
from armis_sdk.entities.asq_rule import AsqRule
from armis_sdk.entities.policy import Policy
from armis_sdk.entities.policy import PolicyAction


pytest_plugins = ["tests.plugins.auto_setup_plugin"]


async def test_list(httpx_mock: pytest_httpx.HTTPXMock):
    httpx_mock.add_response(
        url="https://api.armis.com/v3/policies?limit=100",
        json={
            "items": [
                {
                    "id": 1,
                    "name": "mock_policy",
                    "rule_type": "ACTIVITY",
                    "asq_rule": {"and": ["type:Credentials"]},
                    "is_enabled": True,
                    "labels": ["a"],
                    "actions": [{"type": "ALERT", "params": {"severity": "medium"}}],
                },
            ],
            "next": None,
        },
    )

    policies = [policy async for policy in PoliciesClient().list()]

    assert policies == [
        Policy(
            id=1,
            name="mock_policy",
            rule_type="ACTIVITY",
            asq_rule=AsqRule(and_=["type:Credentials"]),
            is_enabled=True,
            labels=["a"],
            actions=[PolicyAction(type="ALERT", params={"severity": "medium"})],
        )
    ]
