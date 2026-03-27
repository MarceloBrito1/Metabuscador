"""DuckDuckGo search adapter.

Uses the unofficial HTML endpoint (no API key required).
Returns instant-answer / organic results scraped from the DDG JSON endpoint.

Note: DuckDuckGo does not provide a public official search API.  This
adapter uses the ``/html`` page and parses results, which is the most
stable programmatic option available without an API key.
"""

from __future__ import annotations

from typing import List

import httpx

DDG_URL = "https://html.duckduckgo.com/html/"


async def search(query: str, count: int = 10) -> List[dict]:
    """
    Query DuckDuckGo and return a list of result dicts with keys:
    ``title``, ``url``, ``snippet``, ``source``.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    }
    data = {"q": query, "kl": "br-pt"}

    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.post(DDG_URL, data=data, headers=headers)
            response.raise_for_status()
            html = response.text
    except Exception:
        return []

    return _parse_html(html, count)


def _parse_html(html: str, count: int) -> List[dict]:
    """Extract organic results from DuckDuckGo's HTML response."""
    results: List[dict] = []
    # Simple string-based extraction to avoid adding a heavy HTML parser dep.
    # Each result block looks like:
    #   <a class="result__a" href="...">title</a>
    #   <a class="result__snippet">snippet</a>
    import re

    link_pattern = re.compile(
        r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL
    )
    snippet_pattern = re.compile(
        r'class="result__snippet"[^>]*>(.*?)</a>', re.DOTALL
    )

    links = link_pattern.findall(html)
    snippets = [s for s in snippet_pattern.findall(html)]

    clean_tag = re.compile(r"<[^>]+>")

    for i, (url, title) in enumerate(links[:count]):
        snippet = snippets[i] if i < len(snippets) else ""
        results.append(
            {
                "title": clean_tag.sub("", title).strip(),
                "url": url.strip(),
                "snippet": clean_tag.sub("", snippet).strip(),
                "source": "duckduckgo",
            }
        )

    return results
