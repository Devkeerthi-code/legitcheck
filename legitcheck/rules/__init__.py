"""Transparent, hand-written rules for scam patterns common in India.

The ML model learned from mostly US postings (2012-14), so it knows little about
registration fees, Telegram-only HR or Aadhaar requests. These rules carry that knowledge,
and every hit carries the exact phrase so the student can see why it fired.
"""

from __future__ import annotations

from .base import Context, Rule, RuleHit, Severity, Span
from .contact import detect_id_or_bank, detect_messaging_only, detect_personal_email
from .links import detect_suspicious_link
from .money import detect_payment, detect_task_scam, detect_unrealistic_pay
from .pressure import detect_pressure

RULES: tuple[Rule, ...] = (
    Rule(
        "payment_request",
        "Asks you to pay",
        "Real employers pay you. They don't charge registration, training, kit or "
        "'refundable' security fees to give you a job or internship.",
        "Don't pay anything. A genuine company will never need money from you to hire you.",
        detect_payment,
    ),
    Rule(
        "id_or_bank_request",
        "Asks for ID, bank details or OTP early",
        "Aadhaar, PAN and bank details are collected after you join, through an official "
        "HR portal. Asking for them over chat, or before an interview, is how identity and "
        "bank fraud starts. No one legitimate ever needs your OTP, PIN or CVV.",
        "Don't send ID photos or bank details over chat. Never share an OTP or PIN.",
        detect_id_or_bank,
    ),
    Rule(
        "task_scam",
        "Pays you for likes, reviews or 'tasks'",
        "'Like videos and earn' and 'rate hotels' jobs pay small amounts at first, then ask "
        "you to 'prepay' for bigger tasks. That money doesn't come back.",
        "Stop before you deposit anything to 'unlock' tasks or withdraw earnings.",
        detect_task_scam,
    ),
    Rule(
        "messaging_only_contact",
        "Recruiter only on Telegram or WhatsApp",
        "Companies hire through official email and careers portals. Moving you to "
        "Telegram or WhatsApp keeps the conversation off any record they can be held to.",
        "Ask for an interview over an official company email address. Check it from the "
        "company's own website.",
        detect_messaging_only,
    ),
    Rule(
        "personal_email",
        "Company uses a personal email address",
        "A recruiter from a real company writes from the company's own domain (like "
        "name@company.com), not Gmail, Yahoo or Outlook.",
        "Look up the company's real domain on its website and check the sender matches.",
        detect_personal_email,
    ),
    Rule(
        "unrealistic_pay",
        "Pay that's too good for the work",
        "Very high pay per day or week for little work, no experience and no interview is "
        "the hook used in most job scams.",
        "Compare with similar roles on trusted job sites. If it's far above, be careful.",
        detect_unrealistic_pay,
    ),
    Rule(
        "pressure_to_decide",
        "Pressure to decide fast",
        "'Offer valid today only' or 'limited seats' is meant to stop you checking. A real "
        "offer gives you time to read it and ask questions.",
        "Take your time. Pressure is a reason to slow down.",
        detect_pressure,
    ),
    Rule(
        "suspicious_link",
        "Shortened or lookalike link",
        "Short links hide where they go, and lookalike domains (like 'infosys-careers.in') "
        "copy a real company's name to look official.",
        "Don't click. Type the company's real website address yourself.",
        detect_suspicious_link,
    ),
)

RULES_BY_ID = {rule.id: rule for rule in RULES}


def run_rules(text: str, url: str = "", email: str = "") -> list[RuleHit]:
    """Run every rule. Returns hits ordered by severity (high first), then by rule order."""
    ctx = Context(text=text, url=url or "", email=email or "")
    hits = []
    for rule in RULES:
        result = rule.detect(ctx)
        if result:
            severity, spans = result
            hits.append(RuleHit(rule.id, severity, rule.title, rule.why, rule.advice, spans))
    order = {Severity.HIGH: 0, Severity.MEDIUM: 1, Severity.LOW: 2}
    return sorted(hits, key=lambda h: order[h.severity])


__all__ = ["RULES", "RULES_BY_ID", "Context", "RuleHit", "Severity", "Span", "run_rules"]
