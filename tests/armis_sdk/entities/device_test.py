import datetime

from armis_sdk.entities.device import Device


def test_device_instantiation_with_datetime():
    device = Device(first_seen=datetime.datetime(2025, 1, 1), last_seen=datetime.datetime(2025, 6, 1))
    assert device.first_seen == datetime.datetime(2025, 1, 1)
    assert device.last_seen == datetime.datetime(2025, 6, 1)


def test_device_instantiation_with_none_datetimes():
    device = Device()
    assert device.first_seen is None
    assert device.last_seen is None


def test_device_model_json_schema_includes_datetime_fields():
    """datetime.datetime fields must appear in the JSON schema (regression: TYPE_CHECKING import drops them)."""
    schema = Device.model_json_schema()
    props = schema.get("properties", {})
    # Fields use camelCase aliases per BaseEntity's alias_generator
    assert "firstSeen" in props, f"firstSeen missing from schema properties: {sorted(props.keys())}"
    assert "lastSeen" in props, f"lastSeen missing from schema properties: {sorted(props.keys())}"
