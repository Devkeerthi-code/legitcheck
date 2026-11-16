"""Built-in explanations, so the app is complete without any LLM."""

from __future__ import annotations

from .model.predictor import Contribution
from .rules import RuleHit
from .verdict import Verdict

TOKEN_LABELS = {
    "emailtoken": "an email address",
    "urltoken": "a link",
    "phonetoken": "a phone number",
}

_OPENERS = {
    Verdict.HIGH_RISK: "This message has strong signs of a job scam.",
    Verdict.WARNING: "This message has some warning signs worth checking before you reply.",
    Verdict.CONSISTENT: (
        "We didn't find common scam signs, and the wording looks like genuine postings the "
        "model has seen. That doesn't prove it's real, so still run through the checklist."
    ),
}


def readable_term(term: str) -> str:
    """Replace contact tokens in an n-gram: "contact emailtoken" -> "contact [an email address]"."""
    return " ".join(f"[{TOKEN_LABELS[w]}]" if w in TOKEN_LABELS else w for w in term.split())


def template_explanation(verdict: Verdict, hits: list[RuleHit], score: float) -> str:
    parts = [_OPENERS[verdict]]
    for hit in hits[:4]:
        quoted = ", ".join(f'"{m.text}"' for m in hit.matches[:2])
        parts.append(f"{hit.title}: {quoted}. {hit.why}")
    if not hits and verdict != Verdict.CONSISTENT:
        parts.append(
            f"No specific rule fired, but the model scored the wording at {score:.0%}, "
            "which is similar to fake postings it learned from."
        )
    parts.append("You decide. Verify the company yourself before you pay or share anything.")
    return " ".join(parts)


def term_direction(c: Contribution) -> str:
    return "towards_fake" if c.weight > 0 else "towards_genuine"
