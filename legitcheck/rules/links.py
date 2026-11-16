"""Rules about links: URL shorteners, raw IP links, punycode and brand lookalikes."""

from __future__ import annotations

import re

from .base import Context, Severity, Span

SHORTENERS = frozenset(
    {
        "bit.ly",
        "tinyurl.com",
        "goo.gl",
        "t.ly",
        "cutt.ly",
        "is.gd",
        "rb.gy",
        "shorturl.at",
        "tiny.cc",
        "ow.ly",
        "rebrand.ly",
        "s.id",
        "shorte.st",
        "v.gd",
        "bitly.com",
        "tiny.one",
    }
)

# Well-known employers students see impersonated, mapped to domains they really use.
BRANDS: dict[str, frozenset[str]] = {
    "tcs": frozenset({"tcs.com"}),
    "infosys": frozenset({"infosys.com"}),
    "wipro": frozenset({"wipro.com"}),
    "hcl": frozenset({"hcltech.com", "hcl.com"}),
    "accenture": frozenset({"accenture.com"}),
    "cognizant": frozenset({"cognizant.com"}),
    "capgemini": frozenset({"capgemini.com"}),
    "deloitte": frozenset({"deloitte.com"}),
    "amazon": frozenset({"amazon.jobs", "amazon.in", "amazon.com", "amazon.science"}),
    "flipkart": frozenset({"flipkart.com", "flipkartcareers.com"}),
    "google": frozenset({"google.com", "careers.google.com"}),
    "microsoft": frozenset({"microsoft.com"}),
    "techmahindra": frozenset({"techmahindra.com"}),
    "reliance": frozenset({"ril.com", "jio.com", "relianceretail.com"}),
    "zomato": frozenset({"zomato.com"}),
    "swiggy": frozenset({"swiggy.com", "careers.swiggy.com"}),
    "paytm": frozenset({"paytm.com"}),
    "internshala": frozenset({"internshala.com"}),
    "naukri": frozenset({"naukri.com"}),
    "linkedin": frozenset({"linkedin.com"}),
}

URL = re.compile(
    r"\b(?:https?://)?(?P<host>(?:[a-z0-9-]+\.)+[a-z]{2,24}|\d{1,3}(?:\.\d{1,3}){3})"
    r"(?::\d+)?(?P<path>/[^\s<>\"')\]]*)?",
    re.IGNORECASE,
)
_IP = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
# Bare words like "e.g" or "Pvt.Ltd" are not links; require a scheme, www, or a path.
_LOOKS_LIKE_LINK = re.compile(r"^(?:https?://|www\.)|/", re.IGNORECASE)


def registered_domain(host: str) -> str:
    """Last two labels, or three for second-level suffixes like .co.in."""
    labels = host.lower().rstrip(".").split(".")
    if len(labels) >= 3 and labels[-2] in {"co", "ac", "gov", "org", "net", "edu"}:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def levenshtein(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


_DIGIT_SWAP = str.maketrans({"0": "o", "1": "l", "3": "e", "5": "s", "@": "a"})


def lookalike_brand(host: str) -> str | None:
    """Return the brand a host imitates, or None.

    Flags hosts that contain or nearly spell a brand name ("infosys-careers.in",
    "amaz0n-jobs.com", "wipr0.co") but are not one of that brand's real domains.
    """
    host = host.lower()
    domain = registered_domain(host)
    if any(host == d or host.endswith("." + d) for ds in BRANDS.values() for d in ds):
        return None
    tokens = re.split(r"[.\-_]", domain.translate(_DIGIT_SWAP))
    for brand in BRANDS:
        for token in tokens:
            if token == brand or (brand in token and len(brand) >= 4):
                return brand
            if len(brand) >= 5 and len(token) >= 5 and levenshtein(token, brand) == 1:
                return brand
    return None


def is_suspicious_host(host: str) -> bool:
    host = host.lower()
    return (
        registered_domain(host) in SHORTENERS
        or host in SHORTENERS
        or bool(_IP.match(host))
        or "xn--" in host
        or lookalike_brand(host) is not None
    )


def _link_spans(value: str, source: str, require_link_shape: bool) -> list[Span]:
    spans = []
    for m in URL.finditer(value):
        if require_link_shape and not _LOOKS_LIKE_LINK.search(m.group(0)):
            continue
        if "@" in value[max(0, m.start() - 1) : m.start()]:
            continue  # the domain part of an email address, handled by the email rule
        if is_suspicious_host(m.group("host")):
            link = m.group(0).rstrip(".,;:!?")
            spans.append(Span(m.start(), m.start() + len(link), link, source))
    return spans


def detect_suspicious_link(ctx: Context) -> tuple[Severity, list[Span]] | None:
    spans = _link_spans(ctx.text, "text", require_link_shape=True)
    if ctx.url:
        spans += _link_spans(ctx.url, "url", require_link_shape=False)
    return (Severity.MEDIUM, spans) if spans else None
