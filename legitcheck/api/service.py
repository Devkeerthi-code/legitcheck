"""The /check pipeline as plain functions, so it can be tested without HTTP."""

from __future__ import annotations

from dataclasses import asdict

from ..checklist import CHECKLIST
from ..explain import readable_term, template_explanation, term_direction
from ..explain_llm import GeminiExplainer
from ..model.predictor import LegitModel
from ..rules import run_rules
from ..verdict import MIN_WORDS_FOR_MODEL_WARNING, VERDICT_LABELS, decide, model_is_reliable
from .schemas import CheckRequest, CheckResponse

DISCLAIMER = (
    "LegitCheck gives a second opinion from patterns, not a guarantee. It can miss new scams "
    "and can flag genuine offers. Always verify with the company directly. You decide."
)

SHORT_TEXT_NOTE = (
    f"This is a short message (under {MIN_WORDS_FOR_MODEL_WARNING} words). The model learned "
    "from full job postings, so its score counts for less here and the warning-sign rules "
    "matter more."
)


def run_check(model: LegitModel, explainer: GeminiExplainer, req: CheckRequest) -> CheckResponse:
    # The email and URL fields are scored together with the text, as they'd appear in a message.
    scored_text = "\n".join(v for v in (req.text, req.email, req.url) if v)
    score = model.score(scored_text)
    hits = run_rules(req.text, url=req.url or "", email=req.email or "")
    reliable = model_is_reliable(req.text)
    decision = decide(score, hits, model.warn_threshold, model.high_threshold, reliable)

    fallback = template_explanation(decision.verdict, hits, score)
    if req.lang == "en" and not explainer.available:
        rewrite_text, llm_used = fallback, False
    else:
        rewrite = explainer.rewrite(fallback, decision.verdict, hits, score, req.lang)
        rewrite_text, llm_used = rewrite.text, rewrite.used_llm

    return CheckResponse(
        verdict=decision.verdict.value,
        verdict_label=VERDICT_LABELS[decision.verdict],
        reasons=decision.reasons,
        score=round(score, 4),
        thresholds={"warn": round(model.warn_threshold, 4), "high": round(model.high_threshold, 4)},
        rules=[
            {
                "id": h.id,
                "severity": h.severity.value,
                "title": h.title,
                "why": h.why,
                "advice": h.advice,
                "matches": [asdict(m) for m in h.matches],
            }
            for h in hits
        ],
        top_terms=[
            {"term": readable_term(c.term), "weight": c.weight, "direction": term_direction(c)}
            for c in model.contributions(req.text, k=8)
        ],
        checklist=[asdict(item) for item in CHECKLIST],
        explanation=rewrite_text,
        explanation_lang=req.lang if llm_used else "en",
        llm_used=llm_used,
        model_reliable=reliable,
        model_note=None if reliable else SHORT_TEXT_NOTE,
        model_version=model.version,
        disclaimer=DISCLAIMER,
    )
