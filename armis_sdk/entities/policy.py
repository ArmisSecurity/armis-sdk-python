from typing import Any
from typing import Literal

from pydantic import Field

from armis_sdk.core.base_entity import BaseEntity
from armis_sdk.entities.asq_rule import AsqRule


class PolicyAction(BaseEntity):
    """
    A `PolicyAction` is an action that Armis performs when a [Policy][armis_sdk.entities.policy.Policy] matches,
    for example raising an alert or tagging the matching devices.

    Examples:
        An action that raises a medium severity alert.
        ```python
        PolicyAction(type="ALERT", params={"severity": "medium", "title": "Credentials Exposed - HTTP"})
        ```

        An action that tags the matching devices.
        ```python
        PolicyAction(type="TAG", params={"tags": ["exposed"], "endpoint": "ALL"})
        ```
    """

    # ruff: disable[PYI051]
    type: (
        Literal[
            "ALERT",
            "ALERT_CRITICAL",
            "ALERT_HIGH",
            "ALERT_LOW",
            "ALERT_MEDIUM",
            "ARMIS_SCANNER_SCAN",
            "BLOCK",
            "BLOCK_FIREWALL",
            "BLOCK_PANW",
            "BLOCK_WLC",
            "BOUNDARY",
            "CREATE_TICKETS",
            "CUSTOM_ACTION",
            "CUSTOM_PROPERTY",
            "CUSTOM_RISK_FACTOR",
            "CVE_ASSOCIATION_STATUS",
            "DEVICE_GROUP_ASSIGNMENT",
            "ENFORCEMENT",
            "LINK_LAYER_SEGMENTATION",
            "MANAGE_SWITCH_PORT",
            "NETWORK_LAYER_SEGMENTATION",
            "NEXPOSE_SCAN",
            "ORG_PRIORITY",
            "QUALYS_SCAN",
            "RAPID7_INSIGHTVM_SCAN",
            "RISK_FACTOR",
            "SERVICE_NOW_PUSH",
            "TAG",
            "TENABLE_IO_SCAN",
            "TENABLE_SC_SCAN",
            "TORQ_TRIGGER",
            "UNTAG",
        ]
        | str
    )
    # ruff: enable[PYI051]
    """
    The type of the action.

    Example: `ALERT`

    !!! note
        New types may be introduced in the future, so make sure your code can handle types that aren't listed here.
    """

    params: dict[str, Any] = Field(default_factory=dict)
    """
    The parameters of the action. Their shape depends on the action's [`type`][armis_sdk.entities.policy.PolicyAction.type].

    For example, an `ALERT` action contains `severity`, `title`, `endpoint` and `consolidation`,
    while a `TAG` action contains `tags` and `endpoint`.
    """


class Policy(BaseEntity):
    """
    The `Policy` entity represents a policy that raises alerts / performs actions when its rule matches.
    """

    id: int
    """The id of the policy."""

    name: str
    """The name of the policy."""

    rule_type: Literal["ACTIVITY", "DEVICE", "IP_CONNECTION", "VULNERABILITY"]
    """The type of entity the policy's rule is evaluated against."""

    asq_rule: AsqRule
    """The ASQ rule that determines which entities the policy matches."""

    description: str | None = None
    """The description of the policy."""

    is_enabled: bool = False
    """Whether the policy is active."""

    labels: list[str] | None = None
    """The labels of the policy."""

    mitre_attack_labels: list[dict[str, Any]] | None = None
    """The MITRE ATT&CK annotations of the policy."""

    actions: list[PolicyAction] = Field(default_factory=list)
    """The actions to perform when the policy matches."""
