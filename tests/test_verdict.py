from legitcheck.explain import readable_term, template_explanation
from legitcheck.rules import RuleHit, Severity
from legitcheck.verdict import Verdict, decide

WARN, HIGH = 0.2, 0.7


def hit(severity: Severity) -> RuleHit:
    return RuleHit("x", severity, "Title", "Why", "Advice", [])


def test_clean_and_low_score_is_consistent():
    assert decide(0.05, [], WARN, HIGH).verdict == Verdict.CONSISTENT


def test_high_rule_overrides_low_score():
    assert decide(0.01, [hit(Severity.HIGH)], WARN, HIGH).verdict == Verdict.HIGH_RISK


def test_high_score_alone_is_high_risk():
    assert decide(0.9, [], WARN, HIGH).verdict == Verdict.HIGH_RISK


def test_medium_rule_or_warn_score_is_warning():
    assert decide(0.05, [hit(Severity.MEDIUM)], WARN, HIGH).verdict == Verdict.WARNING
    assert decide(0.3, [], WARN, HIGH).verdict == Verdict.WARNING


def test_one_low_rule_is_not_enough_but_two_are():
    assert decide(0.05, [hit(Severity.LOW)], WARN, HIGH).verdict == Verdict.CONSISTENT
    assert decide(0.05, [hit(Severity.LOW)] * 2, WARN, HIGH).verdict == Verdict.WARNING


def test_template_never_says_safe():
    for verdict in Verdict:
        text = template_explanation(verdict, [], 0.1).lower()
        assert "safe" not in text and "you decide" in text


def test_readable_term():
    assert readable_term("contact emailtoken") == "contact [an email address]"
