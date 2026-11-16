"""Combine the model score and the rule hits into one of three verdicts.

There is deliberately no "safe" verdict: a clean result only means the text looks like
genuine postings the model has seen, and the student still has to verify.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from .rules import RuleHit, Severity

# The model learned from full job postings (median ~400 words). Under this length it saw
# few examples, and those were often fake, so short genuine messages score high. Below it,
# the model's warning threshold is ignored and only the high threshold and rules count.
MIN_WORDS_FOR_MODEL_WARNING = 60
_WORD = re.compile(r"\w+")


class Verdict(StrEnum):
    CONSISTENT = "consistent"
    WARNING = "warning"
    HIGH_RISK = "high_risk"


VERDICT_LABELS = {
    Verdict.CONSISTENT: "Looks consistent with genuine postings",
    Verdict.WARNING: "Has warning signs",
    Verdict.HIGH_RISK: "High risk",
}


def model_is_reliable(text: str) -> bool:
    return len(_WORD.findall(text)) >= MIN_WORDS_FOR_MODEL_WARNING


@dataclass(frozen=True)
class Decision:
    verdict: Verdict
    reasons: list[str]


def decide(
    score: float, hits: list[RuleHit], warn: float, high: float, model_reliable: bool = True
) -> Decision:
    """Rules can only raise the verdict, never lower what the model says."""
    reasons: list[str] = []
    severities = [h.severity for h in hits]

    if Severity.HIGH in severities:
        reasons.append("A high-severity warning sign was found.")
    if score >= high:
        reasons.append("The model score is in the high-risk range.")
    if reasons:
        return Decision(Verdict.HIGH_RISK, reasons)

    if Severity.MEDIUM in severities:
        reasons.append("A warning sign was found.")
    if severities.count(Severity.LOW) >= 2:
        reasons.append("Several minor warning signs were found.")
    if score >= warn and model_reliable:
        reasons.append("The model score is above the warning level.")
    if reasons:
        return Decision(Verdict.WARNING, reasons)

    if score >= warn:
        return Decision(
            Verdict.CONSISTENT,
            [
                "No warning signs found. The model score is raised, but it is less reliable on "
                "short messages, so it wasn't used on its own."
            ],
        )
    return Decision(Verdict.CONSISTENT, ["No warning signs found and the model score is low."])
