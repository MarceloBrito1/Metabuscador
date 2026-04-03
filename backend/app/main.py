from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .models import SearchResponse
from .search.aggregator import SearchAggregator
from .search.duckduckgo import DuckDuckGoSearcher
from .search.wikipedia import WikipediaSearcher

app = FastAPI(
    title="Metabuscador",
    description="Meta-search engine that aggregates results from multiple sources.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

aggregator = SearchAggregator(
    searchers=[
        DuckDuckGoSearcher(),
        WikipediaSearcher(),
    ]
)


@app.get("/", tags=["root"])
async def root():
    return {"message": "Metabuscador API", "version": "1.0.0"}


@app.get("/health", tags=["root"])
async def health():
    return {"status": "ok"}


@app.get("/search", response_model=SearchResponse, tags=["search"])
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    max_results: int = Query(
        default=5, ge=1, le=20, description="Max results per search engine"
    ),
):
    results = await aggregator.search(q, max_results_per_engine=max_results)
    return SearchResponse(query=q, results=results, total=len(results))
