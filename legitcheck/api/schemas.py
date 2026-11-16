"""Request and response models (validated by pydantic, shown in the OpenAPI docs)."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(?:\.[\w-]+)+$")
_URL = re.compile(r"^(?:https?://)?[\w.-]+\.[a-z]{2,24}(?::\d+)?(?:/\S*)?$", re.I)

Lang = Literal["en", "hi", "ta", "kn", "te"]
Source = Literal["web", "extension", "api"]
MIN_TEXT, MAX_TEXT = 20, 20_000


class CheckRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "Congratulations! You are selected. Pay the registration fee of Rs 1,999 "
                "to confirm your seat. Contact HR on Telegram @example_hr.",
                "email": "example.hr.team@gmail.com",
                "lang": "en",
                "source": "api",
            }
        }
    )

    text: str = Field(description="The posting, offer letter or message to check.")
    url: str | None = Field(default=None, max_length=2048, description="Link in the offer, if any.")
    email: str | None = Field(default=None, max_length=254, description="Recruiter's email.")
    lang: Lang = Field(default="en", description="Explanation language (non-English needs Gemini).")
    source: Source = "api"

    @field_validator("text")
    @classmethod
    def _text(cls, value: str) -> str:
        value = _CONTROL.sub("", value).strip()
        if len(value) < MIN_TEXT:
            raise ValueError(f"Paste at least {MIN_TEXT} characters so there's something to check.")
        if len(value) > MAX_TEXT:
            raise ValueError(f"That's over {MAX_TEXT:,} characters. Paste just the offer part.")
        return value

    @field_validator("url")
    @classmethod
    def _url(cls, value: str | None) -> str | None:
        value = (value or "").strip()
        if not value:
            return None
        if not _URL.match(value):
            raise ValueError("That doesn't look like a web link.")
        return value

    @field_validator("email")
    @classmethod
    def _email(cls, value: str | None) -> str | None:
        value = (value or "").strip()
        if not value:
            return None
        if not _EMAIL.match(value):
            raise ValueError("That doesn't look like an email address.")
        return value


class MatchOut(BaseModel):
    start: int
    end: int
    text: str
    source: Literal["text", "url", "email"]


class RuleOut(BaseModel):
    id: str
    severity: Literal["high", "medium", "low"]
    title: str
    why: str
    advice: str
    matches: list[MatchOut]


class TermOut(BaseModel):
    term: str
    weight: float
    direction: Literal["towards_fake", "towards_genuine"]


class ChecklistOut(BaseModel):
    id: str
    title: str
    detail: str
    link: str | None = None
    link_label: str | None = None


class Thresholds(BaseModel):
    warn: float
    high: float


class CheckResponse(BaseModel):
    verdict: Literal["consistent", "warning", "high_risk"]
    verdict_label: str
    reasons: list[str]
    score: float = Field(description="Calibrated probability the wording matches fake postings.")
    thresholds: Thresholds
    rules: list[RuleOut]
    top_terms: list[TermOut]
    checklist: list[ChecklistOut]
    explanation: str
    explanation_lang: Lang
    llm_used: bool
    model_reliable: bool = Field(
        description="False for short messages, where the score counts less."
    )
    model_note: str | None
    model_version: str
    disclaimer: str


class FirstUseRequest(BaseModel):
    source: Source = "web"


class HealthResponse(BaseModel):
    status: Literal["ok"]
    model_version: str
    llm_available: bool


class StatsResponse(BaseModel):
    people: int = Field(description="Browsers that used the app at least once (first-use events).")
    checks: int
    by_verdict: dict[str, int]
