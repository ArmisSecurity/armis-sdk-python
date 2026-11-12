import datetime
from typing import Any
from typing import Literal

from pydantic import Field

from armis_sdk.core.base_entity import BaseEntity


class IntegrationCycleStatistics(BaseEntity):
    """Statistics of a single entity type in the last cycle of an integration."""

    entity_type: str
    """The entity type that was synced in the cycle."""

    post_filter_amount: int | None = None
    """The amount of records after filtering."""

    sent_to_armis_amount: int | None = None
    """The amount of records sent to Armis."""

    unique_armis_records_amount: int | None = None
    """The amount of unique Armis records."""


class IntegrationStatistics(BaseEntity):
    """The run statistics of an integration."""

    status: Literal["ACTIVE", "ERROR", "SYNC", "UNKNOWN", "WARNING"] | None = None
    """The status of the integration."""

    error_details: str | None = None
    """Raw error details of the last run."""

    last_successful_cycle_ended: datetime.datetime | None = Field(strict=False, default=None)
    """When the last successful cycle ended."""

    status_created_at: datetime.datetime | None = Field(strict=False, default=None)
    """When the status was first reported."""

    status_changed_at: datetime.datetime | None = Field(strict=False, default=None)
    """When the status last changed."""

    cycle_statistics: list[IntegrationCycleStatistics] | None = None
    """Per-entity-type statistics of the last cycle."""


class Integration(BaseEntity):
    """
    The `Integration` entity represents a configured instance of a data source integration.
    """

    id: int | None = None
    """The id of the integration."""

    name: str | None = None
    """
    The display name of the integration type.

    Example: `CrowdStrike`
    """

    instance_name: str | None = Field(min_length=1, default=None)
    """The name of this integration instance."""

    params: dict[str, Any] | None = None
    """The parameters of the integration. Their shape depends on the integration type."""

    state: Literal["ACTIVE", "DRAFT", "INACTIVE"] | None = None
    """The state of the integration."""

    collector_id: int | None = None
    """The id of the collector associated with the integration."""

    broker_id: int | None = None
    """The id of the broker associated with the integration."""

    creation_time: datetime.datetime | None = Field(strict=False, default=None, frozen=True)
    """When the integration was created. Read-only."""

    params_change_time: datetime.datetime | None = Field(strict=False, default=None, frozen=True)
    """When the parameters were last changed. Read-only."""

    current_state: Literal["IDLE", "INITIALIZING", "RUNNING", "SYNCING_CHANGES", "WAITING_FOR_COLLECTOR"] | None = (
        Field(default=None, frozen=True)
    )
    """The health state of the integration. Read-only."""

    statistics: IntegrationStatistics | None = Field(default=None, frozen=True)
    """The run statistics of the integration. Read-only."""
