"""FastAPI backend for Metabuscador Limpo.

Run with:
    uvicorn main:app --reload
"""

from __future__ import annotations

import asyncio
import os
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

from filters import deduplicate, filter_ads
from limiter import DAILY_LIMIT, consume, get_remaining
from profiles import PROFILE_LABELS, PROFILES, profile_score
from search import bing, duckduckgo, google

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Metabuscador Limpo",
    description=(
        "Meta-search engine that aggregates Google, Bing and DuckDuckGo results, "
        "removes duplicates and ads, and applies configurable search profiles."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=400, description="Search query")
    profile: str = Field(
        "general",
        description=f"Search profile: {', '.join(PROFILES)}",
    )
    user_id: str = Field(
        "anonymous", description="Identifier for the user (for rate limiting)"
    )
    results_per_engine: int = Field(
        10, ge=1, le=20, description="Number of results to request from each engine"
    )


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: str


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    profile: str
    profile_label: str
    remaining_searches: int
    engines_used: List[str]


class LimitResponse(BaseModel):
    user_id: str
    daily_limit: int
    remaining: int
    used: int


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", summary="Health check")
async def root():
    return {"status": "ok", "message": "Metabuscador Limpo is running 🔍"}


@app.post("/search", response_model=SearchResponse, summary="Perform a meta-search")
async def search_endpoint(body: SearchRequest):
    """
    Aggregate results from Bing, DuckDuckGo and Google (if configured),
    filter ads, deduplicate, and sort by the selected profile.
    """
    profile = body.profile if body.profile in PROFILES else "general"

    # Rate-limit check
    if not consume(body.user_id):
        raise HTTPException(
            status_code=429,
            detail=(
                f"Limite diário de {DAILY_LIMIT} buscas atingido para o usuário "
                f"'{body.user_id}'. Tente novamente amanhã."
            ),
        )

    # Fetch from all engines concurrently
    tasks = {
        "bing": bing.search(body.query, body.results_per_engine),
        "duckduckgo": duckduckgo.search(body.query, body.results_per_engine),
        "google": google.search(body.query, body.results_per_engine),
    }

    responses = await asyncio.gather(*tasks.values(), return_exceptions=True)
    engine_results: dict[str, list[dict]] = {}
    for engine, result in zip(tasks.keys(), responses):
        if isinstance(result, list):
            engine_results[engine] = result
        else:
            engine_results[engine] = []

    engines_used = [e for e, r in engine_results.items() if r]

    # Merge
    raw: List[dict] = []
    for res in engine_results.values():
        raw.extend(res)

    # Filter ads then deduplicate
    filtered = filter_ads(raw)
    unique = deduplicate(filtered)

    # Sort by profile score (descending), stable sort preserves original rank
    sorted_results = sorted(
        unique, key=lambda r: profile_score(r.get("url", ""), profile), reverse=True
    )

    return SearchResponse(
        results=[SearchResult(**r) for r in sorted_results],
        total=len(sorted_results),
        profile=profile,
        profile_label=PROFILE_LABELS[profile],
        remaining_searches=get_remaining(body.user_id),
        engines_used=engines_used,
    )


@app.get(
    "/limit/{user_id}",
    response_model=LimitResponse,
    summary="Check daily search limit for a user",
)
async def limit_endpoint(user_id: str):
    """Return how many searches the given user has used/remaining today."""
    remaining = get_remaining(user_id)
    used = DAILY_LIMIT - remaining
    return LimitResponse(
        user_id=user_id,
        daily_limit=DAILY_LIMIT,
        remaining=remaining,
        used=max(0, used),
    )


@app.get("/profiles", summary="List available search profiles")
async def profiles_endpoint():
    """Return the list of supported search profiles."""
    return {
        "profiles": [
            {"id": pid, "label": label} for pid, label in PROFILE_LABELS.items()
        ]
    }
