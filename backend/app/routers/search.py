from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import DailyLimit, SearchHistory, User
from app.routers.auth import get_current_user
from app.schemas import SearchResponse
from app.search.aggregator import aggregate_search
from app.logger import get_logger

router = APIRouter(prefix="/search", tags=["search"])
logger = get_logger(__name__)

def _get_or_create_limit(db: Session, user_id: int) -> DailyLimit:
    today = date.today()
    limit = db.query(DailyLimit).filter(
        DailyLimit.user_id == user_id,
        DailyLimit.search_date == today,
    ).first()
    if not limit:
        limit = DailyLimit(user_id=user_id, search_date=today, count=0)
        db.add(limit)
        db.commit()
        db.refresh(limit)
    return limit

@router.get("/", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=50, description="Results per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    limit = _get_or_create_limit(db, current_user.id)

    if limit.count >= settings.daily_search_limit:
        logger.warning("User %s exceeded daily limit", current_user.username)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily search limit of {settings.daily_search_limit} reached. Try again tomorrow.",
        )

    results = aggregate_search(q, page=page, per_page=per_page)

    limit.count += 1
    db.add(SearchHistory(user_id=current_user.id, query=q, results_count=len(results)))
    db.commit()

    remaining = max(0, settings.daily_search_limit - limit.count)
    logger.info("User %s searched for %r (page=%d) — %d remaining today", current_user.username, q, page, remaining)

    return SearchResponse(
        query=q,
        page=page,
        per_page=per_page,
        total=len(results),
        results=results,
        searches_today=limit.count,
        searches_remaining=remaining,
    )
