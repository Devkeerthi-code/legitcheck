"""Test setup: no real Gemini calls, a throwaway SQLite database, a low rate limit."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

# Set before the app module is imported; load_dotenv() never overrides existing variables.
_TMP = Path(tempfile.mkdtemp(prefix="legitcheck-tests-"))
os.environ["GEMINI_API_KEY"] = ""
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'usage.db').as_posix()}"
os.environ["RATE_LIMIT"] = "8/minute"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"

SCAM = (
    "Congratulations! You are selected for the Work From Home internship at Nexora Talent "
    "Solutions (fictional). Pay the registration fee of Rs 1,999 to confirm your seat today. "
    "Contact HR on Telegram @nexora_hr or nexora.hr.team@gmail.com. Send your Aadhaar card "
    "on WhatsApp before the interview."
)
GENUINE = (
    "Software Engineering Intern at Kestrel Analytics Pvt Ltd (fictional), Bengaluru. Stipend "
    "Rs 25,000 per month. You will build data pipelines in Python with a mentor. There is no "
    "registration fee or deposit at any stage. Apply on our careers page; interviews happen "
    "on Google Meet with the engineering team. careers@kestrelanalytics.in"
)


@pytest.fixture(scope="session")
def model():
    from legitcheck.model.predictor import load_model

    return load_model()


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from legitcheck.api.main import app, limiter

    limiter.reset()
    with TestClient(app) as test_client:
        yield test_client
