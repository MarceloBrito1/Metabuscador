"""Deduplication and ad-filtering helpers for search results."""

from __future__ import annotations

from typing import List
from urllib.parse import urlparse

from profiles import is_ad


def _normalise_url(url: str) -> str:
    """Return a canonical form of a URL for deduplication purposes."""
    try:
        parsed = urlparse(url.strip().lower())
        # drop trailing slash and www. prefix for comparison
        netloc = parsed.netloc.removeprefix("www.")
        path = parsed.path.rstrip("/")
        return f"{netloc}{path}"
    except Exception:
        return url.strip().lower()


def deduplicate(results: List[dict]) -> List[dict]:
    """Remove duplicate results (same normalised URL)."""
    seen: set[str] = set()
    unique: List[dict] = []
    for r in results:
        key = _normalise_url(r.get("url", ""))
        if key and key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


def filter_ads(results: List[dict]) -> List[dict]:
    """Remove results that look like ads or sponsored content."""
    return [r for r in results if not is_ad(r.get("url", ""))]
