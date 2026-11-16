"""Shared types and helpers for the rule layer."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from enum import StrEnum


class Severity(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class Span:
    """A matched phrase. `source` says which input it came from, offsets index into it."""

    start: int
    end: int
    text: str
    source: str = "text"


@dataclass(frozen=True)
class Context:
    text: str
    url: str = ""
    email: str = ""


@dataclass
class RuleHit:
    id: str
    severity: Severity
    title: str
    why: str
    advice: str
    matches: list[Span] = field(default_factory=list)


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    why: str
    advice: str
    detect: Callable[[Context], tuple[Severity, list[Span]] | None]


NEGATION = re.compile(
    r"\b(no|not|never|zero|nil|without|free of|don'?t|doesn'?t|do not|does not|won'?t|will not)\b"
    r"[^.!?\n]{0,30}$",
    re.IGNORECASE,
)


def is_negated(text: str, start: int, window: int = 40) -> bool:
    """True when a negation appears shortly before `start` in the same sentence.

    Catches "we do not charge any registration fee" and "no security deposit".
    """
    return bool(NEGATION.search(text[max(0, start - window) : start]))


def find_spans(pattern: re.Pattern[str], text: str, source: str = "text") -> list[Span]:
    return [Span(m.start(), m.end(), m.group(0), source) for m in pattern.finditer(text)]


def keep_affirmative(spans: Iterable[Span], text: str) -> list[Span]:
    return [s for s in spans if not is_negated(text, s.start)]


def near(text: str, span: Span, pattern: re.Pattern[str], window: int = 80) -> bool:
    """True when `pattern` occurs within `window` characters either side of the span."""
    lo, hi = max(0, span.start - window), min(len(text), span.end + window)
    return bool(pattern.search(text[lo:hi]))


def dedupe_overlaps(spans: Iterable[Span]) -> list[Span]:
    """Drop spans that sit inside an earlier, longer span from the same source."""
    kept: list[Span] = []
    for span in sorted(spans, key=lambda s: (s.source, s.start, -(s.end - s.start))):
        if any(
            k.source == span.source and k.start <= span.start and span.end <= k.end for k in kept
        ):
            continue
        kept.append(span)
    return sorted(kept, key=lambda s: (s.source != "text", s.start))
