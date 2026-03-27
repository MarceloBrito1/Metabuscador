import asyncio
import logging
from urllib.parse import quote_plus

import httpx

from filters import SearchResult

_BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
_DDG_ENDPOINT = "https://api.duckduckgo.com/"
_GOOGLE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"

_TIMEOUT = httpx.Timeout(10.0)
_log = logging.getLogger(__name__)


async def search_bing(query: str, api_key: str | None = None) -> list[SearchResult]:
    """Query the Bing Web Search API and return a list of SearchResult objects.

    Returns an empty list when *api_key* is None or empty.
    """
    if not api_key:
        return []

    params = {"q": query, "count": 10, "mkt": "en-US"}
    headers = {"Ocp-Apim-Subscription-Key": api_key}

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.get(_BING_ENDPOINT, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

    results: list[SearchResult] = []
    for item in data.get("webPages", {}).get("value", []):
        results.append(
            SearchResult(
                title=item.get("name", ""),
                url=item.get("url", ""),
                snippet=item.get("snippet", ""),
            )
        )
    return results


async def search_duckduckgo(query: str) -> list[SearchResult]:
    """Query the DuckDuckGo Instant Answer API and return a list of SearchResult objects.

    Parses the RelatedTopics array; nested topic groups are flattened.
    """
    params = {
        "q": query,
        "format": "json",
        "no_html": "1",
        "skip_disambig": "1",
    }

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.get(_DDG_ENDPOINT, params=params)
        response.raise_for_status()
        data = response.json()

    results: list[SearchResult] = []

    def _parse_topic(topic: dict) -> SearchResult | None:
        url = topic.get("FirstURL", "")
        text = topic.get("Text", "")
        if not url or not text:
            return None
        # Use the first sentence as a title and the rest as snippet
        parts = text.split(". ", 1)
        title = parts[0]
        snippet = parts[1] if len(parts) > 1 else ""
        return SearchResult(title=title, url=url, snippet=snippet)

    for topic in data.get("RelatedTopics", []):
        # Some entries are grouped under a "Topics" sub-list
        if "Topics" in topic:
            for sub in topic["Topics"]:
                item = _parse_topic(sub)
                if item:
                    results.append(item)
        else:
            item = _parse_topic(topic)
            if item:
                results.append(item)

    return results


async def search_google(
    query: str,
    api_key: str | None = None,
    cx: str | None = None,
) -> list[SearchResult]:
    """Query the Google Custom Search JSON API and return a list of SearchResult objects.

    Returns an empty list when *api_key* or *cx* are None or empty.
    """
    if not api_key or not cx:
        return []

    params = {"q": query, "key": api_key, "cx": cx, "num": 10}

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.get(_GOOGLE_ENDPOINT, params=params)
        response.raise_for_status()
        data = response.json()

    results: list[SearchResult] = []
    for item in data.get("items", []):
        results.append(
            SearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
            )
        )
    return results


async def aggregate_results(
    query: str,
    bing_key: str | None = None,
    google_key: str | None = None,
    google_cx: str | None = None,
) -> list[SearchResult]:
    """Call all three search engines concurrently and return their combined results.

    Individual engine failures are caught and logged; the remaining results are
    still returned so a single unreachable API does not break the whole response.
    """
    bing_task = search_bing(query, api_key=bing_key)
    ddg_task = search_duckduckgo(query)
    google_task = search_google(query, api_key=google_key, cx=google_cx)

    bing_results, ddg_results, google_results = await asyncio.gather(
        bing_task, ddg_task, google_task, return_exceptions=True
    )

    combined: list[SearchResult] = []
    for batch in (bing_results, ddg_results, google_results):
        if isinstance(batch, Exception):
            _log.warning("Engine error: %r", batch)
        else:
            combined.extend(batch)

    return combined
