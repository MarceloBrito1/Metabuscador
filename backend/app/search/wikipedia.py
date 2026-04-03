import re
from typing import List

import httpx

from ..models import SearchResult
from .base import BaseSearcher

_TAG_RE = re.compile(r"<[^>]+>")


class WikipediaSearcher(BaseSearcher):
    name = "Wikipedia"
    BASE_URL = "https://en.wikipedia.org/w/api.php"

    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": max_results,
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
        except Exception:
            return []

        results = []
        for item in data.get("query", {}).get("search", []):
            title = item.get("title", "")
            snippet = _TAG_RE.sub("", item.get("snippet", ""))
            url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                    source=self.name,
                )
            )
        return results
