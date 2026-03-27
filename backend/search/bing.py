"""Bing Web Search API adapter.

Requires the environment variable ``BING_API_KEY`` to be set.
Free tier allows up to 3 calls/second and 1 000 calls/month.

API docs: https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/
"""

from __future__ import annotations

import os
from typing import List

import httpx

BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
_API_KEY: str = os.getenv("BING_API_KEY", "")


async def search(query: str, count: int = 10) -> List[dict]:
    """
    Query Bing and return a list of result dicts with keys:
    ``title``, ``url``, ``snippet``, ``source``.
    """
    if not _API_KEY:
        return []

    headers = {"Ocp-Apim-Subscription-Key": _API_KEY}
    params = {
        "q": query,
        "count": min(count, 50),
        "responseFilter": "Webpages",
        "textDecorations": False,
        "textFormat": "Raw",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(BING_ENDPOINT, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception:
        return []

    results: List[dict] = []
    for item in data.get("webPages", {}).get("value", []):
        results.append(
            {
                "title": item.get("name", ""),
                "url": item.get("url", ""),
                "snippet": item.get("snippet", ""),
                "source": "bing",
            }
        )
    return results
