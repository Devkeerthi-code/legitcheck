"""Rules about money: fees and deposits, task-based earning, unrealistic pay."""

from __future__ import annotations

import re

from .base import Context, Severity, Span, dedupe_overlaps, find_spans, keep_affirmative

_FEE_WORDS = (
    r"registration|training|joining|processing|onboarding|verification|application|"
    r"enrol?ment|certification|certificate|kit|documentation|document|interview|security|"
    r"refundable|caution|laptop|uniform|id card|courier|admin|administration|confirmation|"
    r"booking|slot|seat|background check"
)
FEE = re.compile(
    rf"\b(?:{_FEE_WORDS})\s+(?:fees?|charges?|deposit|amount|money|payment)\b"
    r"(?:\s+of\s+(?:rs\.?|inr|₹)\s?[\d,]+(?:\.\d+)?(?:\s?/-)?)?",
    re.IGNORECASE,
)
DEPOSIT = re.compile(
    r"\b(?:security|refundable|caution)\s+deposit\b|\bdeposit\s+(?:of\s+)?(?:rs\.?|inr|₹)\s?[\d,]+",
    re.IGNORECASE,
)
PAY_AMOUNT = re.compile(
    r"\b(?:pay|deposit|transfer|send|submit)\s+(?:a\s+|the\s+|only\s+|just\s+)?"
    r"(?:small\s+|one[- ]time\s+|nominal\s+|refundable\s+)?"
    r"(?:amount\s+of\s+|fees?\s+of\s+)?(?:rs\.?|inr|₹)\s?[\d,]+(?:\.\d+)?(?:\s?/-)?",
    re.IGNORECASE,
)
UPI = re.compile(
    r"\bupi\s*(?:id|number)?\b\s*[:\-]?\s*[\w.\-]+@[a-z]+\b|"
    r"\b(?:paytm|gpay|google pay|phonepe|phone pe)\s+(?:to|on|at)\s+[\d\s]{10,}",
    re.IGNORECASE,
)
HINGLISH_PAY = re.compile(
    r"\b(?:fees?|paise|paisa|rupees?|amount)\s+(?:jama|bhej(?:o|ein|na|iye))\b|"
    r"\bjama\s+(?:karna|karein|karo|kare|kijiye)\b",
    re.IGNORECASE,
)


def detect_payment(ctx: Context) -> tuple[Severity, list[Span]] | None:
    spans = [
        s for p in (FEE, DEPOSIT, PAY_AMOUNT, UPI, HINGLISH_PAY) for s in find_spans(p, ctx.text)
    ]
    spans = keep_affirmative(spans, ctx.text)
    return (Severity.HIGH, dedupe_overlaps(spans)) if spans else None


TASK = re.compile(
    r"\blik(?:e|ing)\s+(?:youtube\s+|instagram\s+|our\s+)?(?:videos?|posts?|reels?|pages?)\b|"
    r"\bsubscrib(?:e|ing)\s+(?:to\s+)?(?:youtube\s+)?channels?\b|"
    r"\b(?:rat(?:e|ing)|review(?:ing)?)\s+(?:hotels?|products?|restaurants?|movies?|apps?)\b|"
    r"\bgoogle\s+maps?\s+reviews?\b|"
    r"\bprepaid\s+tasks?\b|\btask[- ]based\s+(?:job|work|earning)s?\b|"
    r"\b(?:merchant|recharge|optimi[sz]ation|order)\s+tasks?\b|"
    r"\bcommission\s+(?:per|on\s+every|for\s+each)\s+(?:task|order|like|review)\b|"
    r"(?:₹|rs\.?|inr)\s?\d+\s+(?:per|for\s+each|for\s+every)\s+(?:like|task|review|video|post)\b",
    re.IGNORECASE,
)


def detect_task_scam(ctx: Context) -> tuple[Severity, list[Span]] | None:
    spans = keep_affirmative(find_spans(TASK, ctx.text), ctx.text)
    return (Severity.HIGH, dedupe_overlaps(spans)) if spans else None


_AMOUNT = r"(?:₹|rs\.?|inr|\$)\s?(?P<num>\d[\d,]*(?:\.\d+)?)\s?(?P<unit>k|lakh|lakhs|lac)?"
_PERIOD = r"\s?(?:/|per|a|an|every|each)?\s?-?\s?(?P<period>day|daily|week|weekly|hour|hr|month)"
PAY = re.compile(_AMOUNT + _PERIOD + r"\b", re.IGNORECASE)
EASY_MONEY = re.compile(
    r"\b(?:earn|make)\s+(?:money\s+)?(?:easily|daily|instantly|from\s+(?:home|your\s+(?:mobile|phone)))\b|"
    r"\bguaranteed\s+(?:income|earning|returns?|payout)\b|"
    r"\b(?:just|only)\s+\d+\s*(?:-\s*\d+\s*)?(?:hours?|hrs?|minutes?|mins?)\s+(?:a|per)\s+day\b|"
    r"\bno\s+(?:interview|experience|skills?)\s+(?:needed|required)[^.\n]{0,40}(?:earn|₹|rs\.?|salary)",
    re.IGNORECASE,
)
# "Daily income Rs 4,000" puts the period before the amount.
PAY_PERIOD_FIRST = re.compile(
    r"\b(?P<period>daily|weekly|monthly)\s+(?:income|earnings?|salary|pay|payout)\s+(?:of\s+)?"
    + _AMOUNT,
    re.IGNORECASE,
)

# Rough ceilings for student / entry-level work in India (INR). Above these, per period,
# the offer is unusual enough to deserve a second look.
_CEILING = {"hour": 1_000, "day": 2_500, "week": 12_000, "month": 150_000}


def parse_amount(num: str, unit: str | None) -> float:
    value = float(num.replace(",", ""))
    unit = (unit or "").lower()
    if unit == "k":
        value *= 1_000
    elif unit in {"lakh", "lakhs", "lac"}:
        value *= 100_000
    return value


def _period_key(raw: str) -> str:
    raw = raw.lower()
    return {"daily": "day", "weekly": "week", "monthly": "month", "hr": "hour"}.get(raw, raw)


def is_unrealistic(amount: float, period: str, currency_symbol: str) -> bool:
    inr = amount * 85 if currency_symbol == "$" else amount
    return inr > _CEILING[_period_key(period)]


def detect_unrealistic_pay(ctx: Context) -> tuple[Severity, list[Span]] | None:
    spans: list[Span] = []
    matches = [*PAY.finditer(ctx.text), *PAY_PERIOD_FIRST.finditer(ctx.text)]
    for m in matches:
        amount = parse_amount(m.group("num"), m.group("unit"))
        symbol = "$" if "$" in m.group(0) else "₹"
        if is_unrealistic(amount, m.group("period"), symbol):
            spans.append(Span(m.start(), m.end(), m.group(0)))
    spans += find_spans(EASY_MONEY, ctx.text)
    return (Severity.MEDIUM, dedupe_overlaps(spans)) if spans else None
