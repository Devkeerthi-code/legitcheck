"""Engineered features for the gradient-boosting model.

Two groups, because a pasted WhatsApp message has no structured fields:
- TEXT features can be computed from any free text, so they are available when serving.
- STRUCTURED features come from dataset columns (logo, salary_range, ...). They are used
  only to measure how much metadata helps; the served model cannot rely on them.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping

from .rules import Context
from .rules.contact import detect_id_or_bank, detect_messaging_only, detect_personal_email
from .rules.links import detect_suspicious_link
from .rules.money import EASY_MONEY, PAY, detect_payment, detect_task_scam, is_unrealistic
from .rules.money import parse_amount as _parse_amount
from .rules.pressure import detect_pressure
from .text import TEXT_FIELDS

_TOKEN = {
    "url": re.compile(r"#URL_[0-9a-f]+#|https?://|www\.", re.I),
    "email": re.compile(r"#EMAIL_[0-9a-f]+#|\b[\w.+-]+@[\w-]+\.[\w.]+", re.I),
    "phone": re.compile(r"#PHONE_[0-9a-f]+#|(?:\+?91[\s-]?)?\b[6-9]\d{9}\b", re.I),
}
_MONEY = re.compile(r"(?:₹|rs\.?\s?|inr\s?|\$)\s?\d[\d,]*", re.I)
_COMPANY = re.compile(
    r"\b(?:pvt\.?\s*ltd|private limited|limited|llp|inc\.?|llc|gmbh|corp)\b", re.I
)
_WFH = re.compile(
    r"\b(?:work\s+from\s+home|wfh|home[- ]based|from\s+your\s+(?:home|phone))\b", re.I
)
_NO_EXP = re.compile(r"\bno\s+(?:prior\s+)?(?:experience|skills?|qualification)\b", re.I)
_DATA_ENTRY = re.compile(r"\b(?:data\s+entry|typing\s+job|form\s+filling|copy\s+paste)\b", re.I)
_WORD = re.compile(r"\w+")

TEXT_FEATURES = (
    "log_chars",
    "caps_ratio",
    "exclaim_per_100w",
    "has_url",
    "has_email",
    "has_phone",
    "fee_mentions",
    "id_bank_mentions",
    "task_mentions",
    "messaging_mentions",
    "free_email_mentions",
    "suspicious_links",
    "urgency_mentions",
    "easy_money_mentions",
    "unrealistic_pay",
    "money_mentions",
    "company_suffix",
    "work_from_home",
    "no_experience",
    "data_entry",
)
STRUCTURED_FEATURES = (
    "missing_company_profile",
    "has_company_logo",
    "has_questions",
    "telecommuting",
    "missing_requirements",
    "missing_benefits",
    "salary_missing",
    "salary_zero_or_inverted",
    "salary_spread_ratio",
    "missing_employment_type",
    "missing_education",
    "missing_industry",
    "missing_function",
    "missing_location",
)


def _count(result: tuple[object, list[object]] | None) -> int:
    return len(result[1]) if result else 0


def _unrealistic_pay(text: str) -> int:
    for m in PAY.finditer(text):
        symbol = "$" if "$" in m.group(0) else "₹"
        if is_unrealistic(
            _parse_amount(m.group("num"), m.group("unit")), m.group("period"), symbol
        ):
            return 1
    return 0


def text_features(text: str) -> dict[str, float]:
    """Features computable from any free text (posting, email or chat message)."""
    words = _WORD.findall(text)
    letters = [c for c in text if c.isalpha()]
    ctx = Context(text=text)
    return {
        "log_chars": math.log1p(len(text)),
        "caps_ratio": sum(c.isupper() for c in letters) / len(letters) if letters else 0.0,
        "exclaim_per_100w": 100 * text.count("!") / max(len(words), 1),
        "has_url": float(bool(_TOKEN["url"].search(text))),
        "has_email": float(bool(_TOKEN["email"].search(text))),
        "has_phone": float(bool(_TOKEN["phone"].search(text))),
        "fee_mentions": _count(detect_payment(ctx)),
        "id_bank_mentions": _count(detect_id_or_bank(ctx)),
        "task_mentions": _count(detect_task_scam(ctx)),
        "messaging_mentions": _count(detect_messaging_only(ctx)),
        "free_email_mentions": _count(detect_personal_email(ctx)),
        "suspicious_links": _count(detect_suspicious_link(ctx)),
        "urgency_mentions": _count(detect_pressure(ctx)),
        "easy_money_mentions": len(EASY_MONEY.findall(text)),
        "unrealistic_pay": float(_unrealistic_pay(text)),
        "money_mentions": len(_MONEY.findall(text)),
        "company_suffix": float(bool(_COMPANY.search(text))),
        "work_from_home": float(bool(_WFH.search(text))),
        "no_experience": float(bool(_NO_EXP.search(text))),
        "data_entry": float(bool(_DATA_ENTRY.search(text))),
    }


def _is_blank(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def parse_salary_range(value: object) -> tuple[float, float] | None:
    """Parse '35000-40000' into (35000, 40000). Returns None for missing or malformed."""
    if _is_blank(value):
        return None
    parts = str(value).split("-")
    if len(parts) != 2 or not all(p.strip().isdigit() for p in parts):
        return None
    return float(parts[0]), float(parts[1])


def structured_features(record: Mapping[str, object]) -> dict[str, float]:
    """Features from dataset columns. Not available for pasted text."""
    salary = parse_salary_range(record.get("salary_range"))
    low, high = salary if salary else (0.0, 0.0)
    return {
        "missing_company_profile": float(_is_blank(record.get("company_profile"))),
        "has_company_logo": float(record.get("has_company_logo") == 1),
        "has_questions": float(record.get("has_questions") == 1),
        "telecommuting": float(record.get("telecommuting") == 1),
        "missing_requirements": float(_is_blank(record.get("requirements"))),
        "missing_benefits": float(_is_blank(record.get("benefits"))),
        "salary_missing": float(salary is None),
        "salary_zero_or_inverted": float(salary is not None and (high <= 0 or low > high)),
        "salary_spread_ratio": (high / low) if salary and low > 0 else 0.0,
        "missing_employment_type": float(_is_blank(record.get("employment_type"))),
        "missing_education": float(_is_blank(record.get("required_education"))),
        "missing_industry": float(_is_blank(record.get("industry"))),
        "missing_function": float(_is_blank(record.get("function"))),
        "missing_location": float(_is_blank(record.get("location"))),
    }


def raw_posting_text(record: Mapping[str, object]) -> str:
    """Join raw text fields (case and placeholders kept) for the text features."""
    return "\n".join(str(record[f]) for f in TEXT_FIELDS if not _is_blank(record.get(f)))
