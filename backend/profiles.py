from urllib.parse import urlparse

from filters import SearchResult

PROFILES: dict[str, dict] = {
    "scientific": {
        "description": "Prioritizes academic and government sources (.edu, .gov)",
        "boost_domains": set(),
        "boost_tlds": {".edu", ".gov"},
        "boost_score": 10,
    },
    "journalistic": {
        "description": "Prioritizes trusted news outlets",
        "boost_domains": {
            "bbc.com",
            "reuters.com",
            "nytimes.com",
            "theguardian.com",
            "apnews.com",
            "cnn.com",
            "npr.org",
        },
        "boost_tlds": set(),
        "boost_score": 10,
    },
    "shopping": {
        "description": "Prioritizes comparison and review sites",
        "boost_domains": {
            "amazon.com",
            "ebay.com",
            "walmart.com",
            "bestbuy.com",
            "wirecutter.com",
            "rtings.com",
            "g2.com",
        },
        "boost_tlds": set(),
        "boost_score": 10,
    },
}


def get_domain(url: str) -> str:
    """Extract bare domain (without www.) from a URL."""
    host = urlparse(url.lower()).netloc
    return host.removeprefix("www.")


def score_result(result: SearchResult, profile: str) -> int:
    """Return a relevance score for *result* under the given *profile*.

    Returns 10 if the result's domain matches a boosted domain/TLD, else 0.
    Returns 0 for unknown profiles.
    """
    if profile not in PROFILES:
        return 0

    cfg = PROFILES[profile]
    domain = get_domain(result.url)

    if domain in cfg["boost_domains"]:
        return cfg["boost_score"]

    for tld in cfg["boost_tlds"]:
        if domain.endswith(tld):
            return cfg["boost_score"]

    return 0


def apply_profile(results: list[SearchResult], profile: str) -> list[SearchResult]:
    """Sort *results* by profile score (descending).

    Unknown profiles return the list unchanged.
    """
    if profile not in PROFILES:
        return results

    return sorted(results, key=lambda r: score_result(r, profile), reverse=True)
