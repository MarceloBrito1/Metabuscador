from app.search.duckduckgo import DuckDuckGoEngine
from app.schemas import SearchResult
from app.logger import get_logger

logger = get_logger(__name__)

_engines = [DuckDuckGoEngine()]

def aggregate_search(query: str, page: int = 1, per_page: int = 10) -> list[SearchResult]:
    all_results: list[SearchResult] = []
    seen_urls: set[str] = set()

    for engine in _engines:
        try:
            results = engine.search(query, page=page, per_page=per_page)
            for r in results:
                if r.url not in seen_urls:
                    seen_urls.add(r.url)
                    all_results.append(r)
        except Exception as exc:
            logger.error("Engine %s failed: %s", engine.name, exc)

    logger.info("Aggregated %d unique results for query=%r page=%d", len(all_results), query, page)
    return all_results
