"""Optional Gemini rewrite of the explanation. Never decides anything.

Privacy: Gemini receives only the verdict, rule titles and the short matched phrases,
never the full pasted message. Any failure falls back to the template explanation.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass

from .rules import RuleHit
from .verdict import VERDICT_LABELS, Verdict

log = logging.getLogger("legitcheck.llm")

LANGUAGES = {
    "en": "English",
    "hi": "Hindi (Devanagari script)",
    "ta": "Tamil (Tamil script)",
    "kn": "Kannada (Kannada script)",
    "te": "Telugu (Telugu script)",
}
DEFAULT_MODEL = "gemini-3.5-flash-lite"  # fast; a rewrite needs no reasoning model
TIMEOUT_MS = 10_000  # the API rejects deadlines under 10s
# Claims the rewrite must never make, whatever the model returns: calling an offer safe or
# genuine, or stating as fact that it is a scam. Even "cannot say it is safe" is rejected;
# a needless fallback to the template is cheaper than a wrong claim.
_FORBIDDEN = re.compile(
    r"\b(?:definitely|100%|guaranteed|certainly|surely)\s+(?:safe|genuine|legit|a\s+scam|fake)\b|"
    r"\bsafe\b|"
    r"\b(?:is|are|it's|this\s+is)\s+(?:definitely\s+|clearly\s+|obviously\s+)?"
    r"(?:a\s+)?(?:scam|fraud|fake|genuine|legit(?:imate)?)\b",
    re.I,
)


@dataclass(frozen=True)
class Rewrite:
    text: str
    used_llm: bool


def build_prompt(verdict: Verdict, hits: list[RuleHit], score: float, lang: str) -> str:
    facts = {
        "verdict": VERDICT_LABELS[verdict],
        "model_score_percent": round(score * 100),
        "warning_signs": [
            {"sign": h.title, "why": h.why, "phrases": [m.text[:80] for m in h.matches[:3]]}
            for h in hits
        ],
    }
    return (
        "You help Indian students judge job and internship offers. Rewrite the findings below "
        f"as a short, plain explanation in {LANGUAGES[lang]} (max 110 words, no markdown, "
        "no headings). Keep the verdict exactly as given. Describe warning signs only: never "
        "call the offer safe, genuine, fake or a scam, and never use the word 'safe'. Say the "
        "student should verify and decides. Quote the phrases in double quotes "
        "exactly as given, without translating or transliterating them. "
        "End with: never pay to get a job, and report fraud at cybercrime.gov.in or call 1930.\n"
        f"Findings (JSON): {json.dumps(facts, ensure_ascii=False)}"
    )


class GeminiExplainer:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL") or DEFAULT_MODEL
        self._client = None

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def _get_client(self):
        if self._client is None:
            from google import genai
            from google.genai import types

            self._client = genai.Client(
                api_key=self.api_key, http_options=types.HttpOptions(timeout=TIMEOUT_MS)
            )
        return self._client

    def _generate(self, prompt: str) -> str:
        from google.genai import types

        response = self._get_client().models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3, max_output_tokens=600),
        )
        return (response.text or "").strip()

    def rewrite(
        self, fallback: str, verdict: Verdict, hits: list[RuleHit], score: float, lang: str
    ) -> Rewrite:
        if not self.available or lang not in LANGUAGES:
            return Rewrite(fallback, False)
        try:
            text = self._generate(build_prompt(verdict, hits, score, lang))
        except Exception as exc:  # network, quota, auth: the app must keep working
            log.warning("Gemini rewrite failed, using template: %s", type(exc).__name__)
            return Rewrite(fallback, False)
        if not text or len(text) > 2_000 or _FORBIDDEN.search(text):
            return Rewrite(fallback, False)
        return Rewrite(text, True)
