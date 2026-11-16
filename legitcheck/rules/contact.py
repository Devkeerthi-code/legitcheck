"""Rules about how the 'recruiter' contacts you and what they ask you to share."""

from __future__ import annotations

import re

from .base import Context, Severity, Span, dedupe_overlaps, find_spans, keep_affirmative, near

FREE_EMAIL_DOMAINS = frozenset(
    {
        "gmail.com",
        "googlemail.com",
        "yahoo.com",
        "yahoo.co.in",
        "yahoo.in",
        "ymail.com",
        "outlook.com",
        "hotmail.com",
        "live.com",
        "msn.com",
        "rediffmail.com",
        "rediff.com",
        "aol.com",
        "icloud.com",
        "me.com",
        "protonmail.com",
        "proton.me",
        "zohomail.in",
        "mail.com",
        "gmx.com",
        "yandex.com",
        "tutanota.com",
    }
)
EMAIL = re.compile(r"\b[\w.+-]+@(?P<domain>[\w-]+(?:\.[\w-]+)+)\b")


def _free_email_spans(value: str, source: str) -> list[Span]:
    return [
        Span(m.start(), m.end(), m.group(0), source)
        for m in EMAIL.finditer(value)
        if m.group("domain").lower() in FREE_EMAIL_DOMAINS
    ]


def has_company_email(text: str) -> bool:
    return any(m.group("domain").lower() not in FREE_EMAIL_DOMAINS for m in EMAIL.finditer(text))


def detect_personal_email(ctx: Context) -> tuple[Severity, list[Span]] | None:
    spans = _free_email_spans(ctx.text, "text") + _free_email_spans(ctx.email, "email")
    return (Severity.MEDIUM, spans) if spans else None


MESSAGING = re.compile(
    r"\b(?:telegram|whats\s?app|signal app)\b|\bt\.me/[\w]+|\bwa\.me/\d+|"
    r"\btelegram\s*(?:id|@)\s*@?\w+",
    re.IGNORECASE,
)
CONTACT_VERB = re.compile(
    r"\b(?:contact|message|msg|ping|text|dm|chat|reach|connect|join|send|share|hr|recruiter|"
    r"interview|details|group|number|karein|karo|kijiye|karna)\b|\b\d{5}\s?\d{5}\b",
    re.IGNORECASE,
)


def detect_messaging_only(ctx: Context) -> tuple[Severity, list[Span]] | None:
    """HR asks you to move to Telegram/WhatsApp and gives no official company email."""
    if has_company_email(ctx.text) or (ctx.email and has_company_email(ctx.email)):
        return None
    spans = [s for s in find_spans(MESSAGING, ctx.text) if near(ctx.text, s, CONTACT_VERB, 60)]
    spans = keep_affirmative(spans, ctx.text)
    return (Severity.MEDIUM, dedupe_overlaps(spans)) if spans else None


SENSITIVE_ALWAYS = re.compile(
    r"\b(?:otp|one[- ]time password|cvv|atm\s+pin|upi\s+pin|net\s?banking\s+password|"
    r"debit\s+card\s+(?:number|details)|card\s+pin)\b",
    re.IGNORECASE,
)
ID_OR_BANK = re.compile(
    r"\baadh?aa?r(?:\s+card)?(?:\s+(?:number|copy|details|photo))?\b|"
    r"\bpan\s+(?:card|number|no\.?|details)\b|"
    r"\bbank\s+(?:account\s+)?(?:details|number|statement|passbook)\b|"
    r"\b(?:ifsc|account\s+number|cancelled\s+cheque|passbook)\b",
    re.IGNORECASE,
)
ASK = re.compile(
    r"\b(?:send|share|submit|upload|provide|forward|whatsapp|mail|email|fill|give|need|required)\b",
    re.IGNORECASE,
)
EARLY = re.compile(
    r"\bbefore\s+(?:the\s+)?interview\b|\bto\s+(?:confirm|book|reserve|block|secure|lock)\b|"
    r"\bfor\s+(?:verification|registration|selection|shortlisting)\b|\bimmediately\b|\btoday\b|"
    r"\bwithin\s+\d+\s*(?:hours?|hrs?|minutes?|mins?)\b|\bon\s+(?:whats\s?app|telegram)\b",
    re.IGNORECASE,
)
# Normal onboarding: details collected after joining, in person or on an HR portal.
AFTER_JOINING = re.compile(
    r"\bafter\s+(?:you\s+)?join(?:ing)?\b|\bon\s+your\s+first\s+day\b|\bhr\s+portal\b|"
    r"\bat\s+the\s+office\b|\bfor\s+payroll\b",
    re.IGNORECASE,
)


def detect_id_or_bank(ctx: Context) -> tuple[Severity, list[Span]] | None:
    """OTP/PIN/CVV is never legitimate. ID or bank details are high risk when asked early.

    Genuine employers do collect PAN and bank details, but after you join, through an HR
    portal. So a plain mention is medium; paired with an "early" cue it's high.
    """
    always = keep_affirmative(find_spans(SENSITIVE_ALWAYS, ctx.text), ctx.text)
    asked = [s for s in find_spans(ID_OR_BANK, ctx.text) if near(ctx.text, s, ASK, 60)]
    asked = [
        s for s in keep_affirmative(asked, ctx.text) if not near(ctx.text, s, AFTER_JOINING, 80)
    ]
    if not always and not asked:
        return None
    early = any(near(ctx.text, s, EARLY, 120) for s in asked)
    severity = Severity.HIGH if always or early else Severity.MEDIUM
    return severity, dedupe_overlaps(always + asked)
