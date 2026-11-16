"""Text cleaning shared by training and the API, so both see identical input."""

from __future__ import annotations

import hashlib
import html
import re
from collections.abc import Mapping

TEXT_FIELDS = ("title", "company_profile", "description", "requirements", "benefits")

# The Kaggle dataset anonymises contacts as #URL_<hash>#, #EMAIL_<hash>#, #PHONE_<hash>#.
_PLACEHOLDER = re.compile(r"#(URL|EMAIL|PHONE)_[0-9a-f]+#", re.IGNORECASE)
_URL = re.compile(r"(?:https?://|www\.)\S+|\b[a-z0-9-]+\.(?:ly|gl|gd|to|me|in|com|io|co)/\S*", re.I)
_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
_PHONE = re.compile(r"(?:\+?91[\s-]?)?\b[6-9]\d{4}[\s-]?\d{5}\b|\+\d[\d\s-]{8,14}\d")
_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")


def normalise_contacts(text: str) -> str:
    """Replace real or anonymised contacts with stable tokens.

    Raw URLs/emails/phones are unique per posting and would only add noise; whether a
    contact is present at all is the useful signal, so both data sources map to one token.
    """
    text = _PLACEHOLDER.sub(lambda m: f" {m.group(1).lower()}token ", text)
    text = _EMAIL.sub(" emailtoken ", text)
    text = _URL.sub(" urltoken ", text)
    return _PHONE.sub(" phonetoken ", text)


def clean_text(text: str | None) -> str:
    """Lowercase, unescape HTML, strip tags, normalise contacts and whitespace."""
    if not text:
        return ""
    text = html.unescape(str(text))
    text = _TAG.sub(" ", text)
    text = normalise_contacts(text)
    return _SPACE.sub(" ", text).strip().lower()


def combine_fields(record: Mapping[str, object]) -> str:
    """Join the posting's text fields into one document for the text model."""
    parts = []
    for field in TEXT_FIELDS:
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            parts.append(clean_text(value))
    return " \n ".join(parts)


def dedupe_key(text: str) -> str:
    """Hash of the text with punctuation and spacing removed, to find re-posted ads."""
    squashed = re.sub(r"\W+", "", text.lower())
    return hashlib.sha1(squashed.encode("utf-8")).hexdigest()
