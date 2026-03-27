import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from engines import aggregate_results
from filters import clean_results
from profiles import apply_profile
from usage import DAILY_LIMIT, check_limit, get_usage, increment_usage

app = FastAPI(
    title="Metabuscador Limpo",
    description="A clean meta-search engine aggregating Google, Bing, and DuckDuckGo.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/search")
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    profile: str = Query("general", description="Search profile (scientific, journalistic, shopping, general)"),
    user_id: str = Query("anonymous", description="User identifier for rate limiting"),
):
    """Perform a meta-search across all configured engines.

    Returns filtered, deduplicated, and profile-sorted results together with
    the caller's current usage statistics.
    """
    if not check_limit(user_id):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Daily search limit reached",
                "limit": DAILY_LIMIT,
                "user_id": user_id,
            },
        )

    bing_key = os.environ.get("BING_API_KEY")
    google_key = os.environ.get("GOOGLE_API_KEY")
    google_cx = os.environ.get("GOOGLE_CX")

    raw_results = await aggregate_results(
        q,
        bing_key=bing_key,
        google_key=google_key,
        google_cx=google_cx,
    )

    cleaned = clean_results(raw_results)
    profiled = apply_profile(cleaned, profile)

    usage_count = increment_usage(user_id)
    remaining = max(0, DAILY_LIMIT - usage_count)

    return {
        "results": [
            {
                "title": r.title,
                "url": r.url,
                "snippet": r.snippet,
            }
            for r in profiled
        ],
        "profile": profile,
        "count": usage_count,
        "remaining": remaining,
    }


@app.get("/usage/{user_id}")
async def usage(user_id: str):
    """Return the current daily usage statistics for *user_id*."""
    count = get_usage(user_id)
    remaining = max(0, DAILY_LIMIT - count)
    return {
        "user_id": user_id,
        "count": count,
        "limit": DAILY_LIMIT,
        "remaining": remaining,
    }
