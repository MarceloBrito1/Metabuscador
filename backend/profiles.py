"""Search profiles that filter and prioritise results by domain category."""

from __future__ import annotations

from typing import List


# ---------------------------------------------------------------------------
# Domain / keyword lists per profile
# ---------------------------------------------------------------------------

SCIENTIFIC_PRIORITY = [
    ".edu", ".gov", "arxiv.org", "pubmed.ncbi.nlm.nih.gov",
    "scholar.google", "sciencedirect.com", "nature.com", "springer.com",
    "researchgate.net", "jstor.org", "ncbi.nlm.nih.gov", "ieee.org",
    "acs.org", "plos.org", "biorxiv.org", "medrxiv.org",
]

JOURNALISTIC_PRIORITY = [
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "theguardian.com",
    "nytimes.com", "washingtonpost.com", "economist.com", "ft.com",
    "bloomberg.com", "cnn.com", "npr.org", "propublica.org",
    "folha.uol.com.br", "estadao.com.br", "g1.globo.com", "agenciabrasil.ebc.com.br",
    "valor.com.br", "uol.com.br",
]

SHOPPING_PRIORITY = [
    "amazon.com", "amazon.com.br", "mercadolivre.com.br", "shopee.com.br",
    "americanas.com.br", "magazineluiza.com.br", "kabum.com.br",
    "buscape.com.br", "zoom.com.br", "bondfaro.com.br",
    "pcmag.com", "rtings.com", "wirecutter.com", "thewirecutter.com",
]

# Ad / sponsored patterns to filter out
AD_PATTERNS = [
    "doubleclick.net", "googleadservices.com", "googlesyndication.com",
    "adnxs.com", "ads.yahoo.com", "bing.com/aclk", "taboola.com",
    "outbrain.com", "criteo.com", "smartadserver.com",
    "/aclk?", "?utm_source=", "sponsored=true",
]


def _domain_in(url: str, domains: List[str]) -> bool:
    url_lower = url.lower()
    return any(d in url_lower for d in domains)


def is_ad(url: str) -> bool:
    """Return True if the URL looks like an advertisement."""
    return _domain_in(url, AD_PATTERNS)


def profile_score(url: str, profile: str) -> int:
    """
    Return a priority score for sorting:
      higher → appears earlier in results.
    """
    profile = (profile or "general").lower()
    if profile == "scientific":
        return 2 if _domain_in(url, SCIENTIFIC_PRIORITY) else 0
    if profile == "journalistic":
        return 2 if _domain_in(url, JOURNALISTIC_PRIORITY) else 0
    if profile == "shopping":
        return 2 if _domain_in(url, SHOPPING_PRIORITY) else 0
    return 0


PROFILE_LABELS = {
    "general": "Geral",
    "scientific": "Científico 🔬",
    "journalistic": "Jornalístico 📰",
    "shopping": "Compras 🛒",
}

PROFILES = list(PROFILE_LABELS.keys())
