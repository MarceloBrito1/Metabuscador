import asyncio
from typing import List

from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException

from ..models import SearchResult
from .base import BaseSearcher


class DuckDuckGoSearcher(BaseSearcher):
    name = "DuckDuckGo"

    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        try:
            results_raw = await asyncio.to_thread(self._fetch, query, max_results)
            return results_raw
        except Exception:
            return []

    def _fetch(self, query: str, max_results: int) -> List[SearchResult]:
        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append(
                        SearchResult(
                            title=r.get("title", ""),
                            url=r.get("href", ""),
                            snippet=r.get("body", ""),
                            source=self.name,
                        )
                    )
        except DuckDuckGoSearchException:
            pass
        return results
