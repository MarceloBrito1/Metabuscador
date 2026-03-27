"""Google Custom Search JSON API adapter.

Requires both ``GOOGLE_API_KEY`` and ``GOOGLE_CSE_ID`` environment variables.

Free tier: 100 queries/day.
API docs: https://developers.google.com/custom-search/v1/overview
"""

from __future__ import annotations

import os
from typing import List

import httpx

GOOGLE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"
_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
_CSE_ID: str = os.getenv("GOOGLE_CSE_ID", "")


async def search(query: str, count: int = 10) -> List[dict]:
    """
    Query Google Custom Search and return a list of result dicts with keys:
    ``title``, ``url``, ``snippet``, ``source``.
    """
    if not _API_KEY or not _CSE_ID:
        return []

    # Google CSE returns at most 10 per request; we cap here too.
    params = {
        "key": _API_KEY,
        "cx": _CSE_ID,
        "q": query,
        "num": min(count, 10),
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(GOOGLE_ENDPOINT, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception:
        return []

    results: List[dict] = []
    for item in data.get("items", []):
        results.append(
            {
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source": "google",
            }
        )
    return results
