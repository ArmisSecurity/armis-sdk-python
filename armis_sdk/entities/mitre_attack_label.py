from typing import Literal

from armis_sdk.core.base_entity import BaseEntity


class MitreAttackLabel(BaseEntity):
    """A MITRE ATT&CK annotation."""

    matrix: Literal["ENTERPRISE", "ICS", "MOBILE"]
    """The MITRE ATT&CK matrix family the label belongs to."""

    tactic: str | None = None
    """
    The high-level adversary objective.

    Example: `Initial Access`
    """

    technique: str | None = None
    """
    The specific adversary technique used to achieve the tactic.

    Example: `Phishing`
    """

    sub_technique: str | None = None
    """
    The sub-technique under the parent technique.

    Example: `Spearphishing Attachment`
    """
