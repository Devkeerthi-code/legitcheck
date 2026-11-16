"""FastAPI app. Run locally: uvicorn legitcheck.api.main:app --reload

Submitted text is processed in memory and never stored or logged.
"""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .. import __version__
from ..explain_llm import GeminiExplainer
from ..model.predictor import load_model
from .schemas import (
    CheckRequest,
    CheckResponse,
    FirstUseRequest,
    HealthResponse,
    StatsResponse,
)
from .service import run_check
from .usage import UsageStore

load_dotenv()  # local development; on Render/HF the variables come from the dashboard
log = logging.getLogger("legitcheck.api")
MAX_BODY_BYTES = 64 * 1024
RATE_LIMIT = os.getenv("RATE_LIMIT", "20/minute;200/day")


def client_ip(request: Request) -> str:
    """First X-Forwarded-For hop (Render/HF put a proxy in front), else the socket address."""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


limiter = Limiter(key_func=client_ip, default_limits=[])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.model = load_model()  # once, at startup
    app.state.explainer = GeminiExplainer()
    app.state.usage = UsageStore()
    try:
        app.state.usage.migrate()
    except Exception as exc:
        log.warning("usage database unavailable, counts disabled: %s", type(exc).__name__)
    yield


app = FastAPI(
    title="LegitCheck API",
    version=__version__,
    summary="Checks job and internship offers for scam warning signs. Stores no submitted text.",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


def _allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
    return [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]


def _extension_origin_regex() -> str:
    ext_id = os.getenv("EXTENSION_ID", "").strip()
    return f"chrome-extension://{ext_id}" if ext_id else r"chrome-extension://[a-p]{32}"


app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_origin_regex=_extension_origin_regex(),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    expose_headers=["Retry-After"],
    max_age=600,
)


@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > MAX_BODY_BYTES:
        return JSONResponse({"detail": "Request too large."}, status_code=413)
    return await call_next(request)


@app.exception_handler(RateLimitExceeded)
async def rate_limited(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        {"detail": "Too many checks from your network. Please wait a minute and try again."},
        status_code=429,
        headers={"Retry-After": "60"},
    )


@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health(request: Request) -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_version=request.app.state.model.version,
        llm_available=request.app.state.explainer.available,
    )


@app.post("/check", response_model=CheckResponse, tags=["check"])
@limiter.limit(RATE_LIMIT)
def check(request: Request, body: CheckRequest) -> CheckResponse:
    """Check a posting or message. Returns a verdict, the score, every rule hit with the exact
    phrase, top contributing words, an explanation and the verification checklist."""
    state = request.app.state
    result = run_check(state.model, state.explainer, body)
    state.usage.safe_increment(body.source, f"check_{result.verdict}")
    return result


@app.post("/events/first-use", status_code=204, tags=["meta"])
@limiter.limit("5/minute")
def first_use(request: Request, body: FirstUseRequest) -> None:
    """Counted once per browser (the web app keeps a local flag). No identifiers are sent."""
    request.app.state.usage.safe_increment(body.source, "first_use")


@app.get("/stats", response_model=StatsResponse, tags=["meta"])
@limiter.limit("30/minute")
def stats(request: Request) -> StatsResponse:
    try:
        totals = request.app.state.usage.totals()
    except Exception:
        totals = {}
    by_verdict = {v: totals.get(f"check_{v}", 0) for v in ("consistent", "warning", "high_risk")}
    return StatsResponse(
        people=totals.get("first_use", 0), checks=sum(by_verdict.values()), by_verdict=by_verdict
    )
