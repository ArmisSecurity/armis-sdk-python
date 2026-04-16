from armis_sdk.entities.asq_rule import AsqRule


def test_asq_rule_nested():
    inner = AsqRule(or_=["asq2", "asq3"])
    outer = AsqRule(and_=["asq1", inner])
    assert outer.and_ == ["asq1", inner]


def test_asq_rule_from_asq():
    rule = AsqRule.from_asq("deviceName:MyDevice")
    assert rule.or_ == ["deviceName:MyDevice"]
