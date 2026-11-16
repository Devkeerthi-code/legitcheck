import json
from pathlib import Path

import pytest

from legitcheck.rules import Severity, run_rules
from legitcheck.rules.base import is_negated
from legitcheck.rules.links import levenshtein, lookalike_brand, registered_domain
from legitcheck.rules.money import is_unrealistic, parse_amount

SYNTHETIC = Path(__file__).resolve().parents[1] / "data" / "synthetic" / "india_offers.jsonl"


def ids(text: str, **kw) -> dict[str, Severity]:
    return {h.id: h.severity for h in run_rules(text, **kw)}


def phrases(text: str, rule_id: str, **kw) -> list[str]:
    hit = next(h for h in run_rules(text, **kw) if h.id == rule_id)
    return [m.text for m in hit.matches]


# ---- payment ----
@pytest.mark.parametrize(
    "text",
    [
        "Pay the registration fee of Rs 1,999 to confirm.",
        "A refundable security deposit is required.",
        "Kindly transfer Rs 2,500 for your laptop.",
        "Training fees must be paid before joining.",
        "Send to UPI id jobs.hr@okaxis",
        "Joining ke liye 1500 registration fees jama karna hoga",
    ],
)
def test_payment_requests_are_high(text):
    assert ids(text).get("payment_request") == Severity.HIGH


@pytest.mark.parametrize(
    "text",
    [
        "There is no registration fee at any stage.",
        "We do not charge any training fee or deposit.",
        "Never pay a security deposit to anyone.",
    ],
)
def test_negated_fee_statements_do_not_fire(text):
    assert "payment_request" not in ids(text)


def test_payment_span_is_the_exact_phrase():
    text = "Hi. Pay the registration fee of Rs 1,999 today."
    (span,) = next(h for h in run_rules(text) if h.id == "payment_request").matches
    assert text[span.start : span.end] == span.text == "registration fee of Rs 1,999"


# ---- ID / bank ----
def test_otp_is_always_high():
    assert ids("Please share the OTP you received.")["id_or_bank_request"] == Severity.HIGH


def test_id_before_interview_is_high():
    text = "Send your Aadhaar card and PAN card before the interview."
    assert ids(text)["id_or_bank_request"] == Severity.HIGH


def test_plain_bank_request_is_medium():
    assert ids("Please share your bank account details.")["id_or_bank_request"] == Severity.MEDIUM


def test_onboarding_after_joining_does_not_fire():
    text = "After joining, you'll submit your PAN and bank account details on the HR portal."
    assert "id_or_bank_request" not in ids(text)


def test_never_share_otp_does_not_fire():
    assert "id_or_bank_request" not in ids("Never share OTPs with anyone, including us.")


# ---- task scams ----
@pytest.mark.parametrize(
    "text",
    ["Like YouTube videos and earn", "rate hotels on maps", "buy prepaid tasks", "Rs 50 per like"],
)
def test_task_scams(text):
    assert ids(text).get("task_scam") == Severity.HIGH


# ---- messaging ----
def test_telegram_only_contact():
    assert "messaging_only_contact" in ids("Contact our HR on Telegram @hr_desk for the interview.")


def test_messaging_with_company_email_is_fine():
    text = "Invite from recruiting@lattice.in. You can also WhatsApp me if you're late."
    assert "messaging_only_contact" not in ids(text)


def test_word_telegram_alone_is_fine():
    assert "messaging_only_contact" not in ids("Our product integrates with Telegram bots.")


# ---- personal email ----
def test_free_email_in_text_and_field():
    assert phrases("Mail hr.team@gmail.com", "personal_email") == ["hr.team@gmail.com"]
    hit = next(
        h for h in run_rules("We are hiring.", email="x@yahoo.co.in") if h.id == "personal_email"
    )
    assert hit.matches[0].source == "email"


def test_company_email_is_fine():
    assert "personal_email" not in ids("Mail careers@kestrel.in")


# ---- pay ----
def test_parse_amount_units():
    assert parse_amount("50", "k") == 50_000
    assert parse_amount("1.5", "lakh") == 150_000
    assert parse_amount("12,000", None) == 12_000


def test_unrealistic_thresholds():
    assert is_unrealistic(5_000, "day", "₹")
    assert not is_unrealistic(800, "day", "₹")
    assert is_unrealistic(500, "week", "$")


def test_normal_stipend_does_not_fire():
    assert "unrealistic_pay" not in ids("Stipend Rs 20,000 per month, Rs 180 per hour for shifts.")


def test_period_first_amount():
    assert "unrealistic_pay" in ids("Daily income Rs 4,000 guaranteed")


# ---- pressure ----
def test_single_urgency_is_low_and_money_urgency_is_medium():
    assert ids("Offer valid only today.")["pressure_to_decide"] == Severity.LOW
    assert ids("Pay the amount within 2 hours.")["pressure_to_decide"] == Severity.MEDIUM


def test_urgent_hiring_alone_is_fine():
    assert "pressure_to_decide" not in ids("Urgent hiring: accounts executive, Chennai.")


# ---- links ----
def test_shortener_and_lookalike_links():
    found = phrases("Apply bit.ly/abc or https://infosys-careers.in/apply.", "suspicious_link")
    assert found == ["bit.ly/abc", "https://infosys-careers.in/apply"]


def test_url_field_is_checked():
    hit = next(
        h for h in run_rules("See link", url="http://103.4.5.6/form") if h.id == "suspicious_link"
    )
    assert hit.matches[0].source == "url"


def test_real_brand_domains_are_fine():
    assert lookalike_brand("careers.wipro.com") is None
    assert lookalike_brand("amazon.jobs") is None
    assert "suspicious_link" not in ids("Track it at https://careers.wipro.com/status")


def test_lookalikes():
    assert lookalike_brand("amaz0n-jobs.com") == "amazon"
    assert lookalike_brand("wipr0.co") == "wipro"
    assert lookalike_brand("kestrelanalytics.in") is None


def test_email_domain_is_not_treated_as_link():
    assert "suspicious_link" not in ids("Write to jobs@infosys-careers.in")


def test_helpers():
    assert registered_domain("a.b.example.co.in") == "example.co.in"
    assert levenshtein("wipro", "wipr0") == 1
    assert is_negated("we do not charge any ", len("we do not charge any "))


# ---- synthetic dev set: what the rules were written against ----
def _dev_records():
    with SYNTHETIC.open(encoding="utf-8") as handle:
        records = [json.loads(line) for line in handle]
    assert all(r["synthetic"] for r in records)
    return [r for r in records if r["split"] == "dev"]


@pytest.mark.parametrize("record", _dev_records(), ids=lambda r: r["id"])
def test_synthetic_dev_examples(record):
    found = ids(record["text"], url=record["url"], email=record["email"])
    if record["label"] == "scam":
        assert set(record["expected_rules"]) <= set(found)
    else:
        assert not found, f"false alarm on a genuine example: {found}"
