"""The 'How to verify' checklist shown with every verdict, including clean ones."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChecklistItem:
    id: str
    title: str
    detail: str
    link: str | None = None
    link_label: str | None = None


CHECKLIST: tuple[ChecklistItem, ...] = (
    ChecklistItem(
        "careers_page",
        "Find the company's official careers page",
        "Search for the company yourself instead of using links in the message, and check the "
        "role is listed there.",
    ),
    ChecklistItem(
        "never_pay",
        "Never pay to get a job",
        "No registration, training, kit or 'refundable' deposit. Real employers pay you, not "
        "the other way round.",
    ),
    ChecklistItem(
        "email_domain",
        "Check the HR email domain",
        "The sender's address should end in the company's own website domain, not gmail.com, "
        "yahoo.com or outlook.com.",
    ),
    ChecklistItem(
        "search_scam",
        'Search the company name with "scam"',
        "Look for other students' experiences and reviews before you reply or share anything.",
    ),
    ChecklistItem(
        "report",
        "Report fraud",
        "If you've been asked for money or already paid, report it at cybercrime.gov.in or call "
        "the 1930 helpline as soon as possible.",
        "https://cybercrime.gov.in",
        "cybercrime.gov.in",
    ),
)
