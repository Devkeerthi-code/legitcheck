"""Rule about pressure to decide or pay quickly."""

from __future__ import annotations

import re

from .base import Context, Severity, Span, dedupe_overlaps, find_spans

URGENCY = re.compile(
    r"\b(?:offer|seats?|slots?|this\s+opportunity|link)\s+(?:is\s+|are\s+)?"
    r"(?:valid|available|open|active)\s+(?:only\s+)?(?:for\s+)?"
    r"(?:today|till\s+(?:tonight|today|midnight)|\d+\s*(?:hours?|hrs?|minutes?|mins?))\b|"
    r"\blimited\s+(?:seats?|slots?|vacancies|openings)\b|"
    r"\b(?:seats?|slots?|vacancies|openings)\s+(?:are\s+)?limited\b|"
    r"\bdo\s+it\s+(?:immediately|right\s+now|now|today)\b|"
    r"\bor\s+(?:your\s+)?(?:offer|selection|seat)\s+will\s+be\s+(?:cancelled|canceled|withdrawn)\b|"
    r"\bonly\s+\d+\s+(?:seats?|slots?|positions?|vacancies)\s+(?:left|remaining)\b|"
    r"\bwithin\s+(?:the\s+next\s+)?\d+\s*(?:hours?|hrs?|minutes?|mins?)\b|"
    r"\b(?:pay|confirm|respond|reply|register)\s+(?:immediately|right\s+now|asap|today)\b|"
    r"\blast\s+date\s+(?:is\s+)?today\b|\bact\s+(?:now|fast|quickly)\b|\bhurry\b|"
    r"\bexpires?\s+(?:today|tonight|in\s+\d+)\b|\bbefore\s+(?:the\s+)?(?:offer|seat)s?\s+(?:is\s+|are\s+)?(?:gone|filled|closed)\b",
    re.IGNORECASE,
)
# Repeated urgency or urgency tied to payment is a stronger sign than "urgent hiring".
_MONEY_NEAR = re.compile(r"\b(?:pay|fee|fees|deposit|₹|rs\.?|amount)\b", re.IGNORECASE)


def detect_pressure(ctx: Context) -> tuple[Severity, list[Span]] | None:
    spans = dedupe_overlaps(find_spans(URGENCY, ctx.text))
    if not spans:
        return None
    tied_to_money = any(
        _MONEY_NEAR.search(ctx.text[max(0, s.start - 80) : s.end + 80]) for s in spans
    )
    severity = Severity.MEDIUM if tied_to_money or len(spans) >= 2 else Severity.LOW
    return severity, spans
