from dataclasses import dataclass, field
from urllib.parse import urlparse

KNOWN_AD_DOMAINS = {
    "doubleclick.net",
    "googleadservices.com",
    "googlesyndication.com",
    "adclick.g.doubleclick.net",
    "pagead2.googlesyndication.com",
    "ads.yahoo.com",
    "adtech.de",
    "advertising.com",
    "adblade.com",
    "outbrain.com",
    "taboola.com",
    "revcontent.com",
    "zergnet.com",
}


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    is_ad: bool = field(default=False)


def _normalize_url(url: str) -> str:
    """Normalize a URL for deduplication: lowercase, strip www., strip trailing slash."""
    parsed = urlparse(url.lower().strip())
    host = parsed.netloc.removeprefix("www.")
    path = parsed.path.rstrip("/")
    # Reconstruct a canonical form (scheme + host + path + query)
    normalized = host + path
    if parsed.query:
        normalized += "?" + parsed.query
    return normalized


def get_domain(url: str) -> str:
    """Return the bare domain (without www.) from a URL."""
    host = urlparse(url.lower()).netloc
    return host.removeprefix("www.")


def remove_duplicates(results: list[SearchResult]) -> list[SearchResult]:
    """Remove duplicate results based on normalized URL, keeping first occurrence."""
    seen: set[str] = set()
    unique: list[SearchResult] = []
    for result in results:
        key = _normalize_url(result.url)
        if key not in seen:
            seen.add(key)
            unique.append(result)
    return unique


def remove_ads(results: list[SearchResult]) -> list[SearchResult]:
    """Remove results flagged as ads or whose URL belongs to a known ad domain."""
    clean: list[SearchResult] = []
    for result in results:
        if result.is_ad:
            continue
        if get_domain(result.url) in KNOWN_AD_DOMAINS:
            continue
        clean.append(result)
    return clean


def clean_results(results: list[SearchResult]) -> list[SearchResult]:
    """Apply remove_ads then remove_duplicates and return cleaned results."""
    return remove_duplicates(remove_ads(results))
