from duckduckgo_search import DDGS
from app.schemas import SearchResult
from app.search.base import BaseSearchEngine
from app.logger import get_logger

logger = get_logger(__name__)

class DuckDuckGoEngine(BaseSearchEngine):
    name = "DuckDuckGo"

    def search(self, query: str, page: int = 1, per_page: int = 10) -> list[SearchResult]:
        try:
            offset = (page - 1) * per_page
            results = []
            with DDGS() as ddgs:
                for i, r in enumerate(ddgs.text(query, max_results=offset + per_page)):
                    if i < offset:
                        continue
                    results.append(
                        SearchResult(
                            title=r.get("title", ""),
                            url=r.get("href", ""),
                            snippet=r.get("body", ""),
                            source=self.name,
                        )
                    )
            logger.info("DuckDuckGo returned %d results for query=%r page=%d", len(results), query, page)
            return results
        except Exception as exc:
            logger.error("DuckDuckGo search failed for query=%r: %s", query, exc)
            return []
