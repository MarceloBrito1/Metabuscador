import asyncio
from typing import List

from ..models import SearchResult
from .base import BaseSearcher


class SearchAggregator:
    """Runs all searchers concurrently and deduplicates results by URL."""

    def __init__(self, searchers: List[BaseSearcher]) -> None:
        self.searchers = searchers

    async def search(
        self, query: str, max_results_per_engine: int = 5
    ) -> List[SearchResult]:
        tasks = [
            searcher.search(query, max_results=max_results_per_engine)
            for searcher in self.searchers
        ]
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)

        seen_urls: set[str] = set()
        all_results: List[SearchResult] = []

        for results in results_lists:
            if isinstance(results, Exception):
                continue
            for result in results:
                if result.url and result.url not in seen_urls:
                    seen_urls.add(result.url)
                    all_results.append(result)

        return all_results
