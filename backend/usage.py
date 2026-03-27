import threading
from datetime import date

DAILY_LIMIT: int = 100

# In-memory store: { user_id: {"count": int, "date": date} }
_usage: dict[str, dict] = {}
_lock = threading.Lock()


def get_usage(user_id: str) -> int:
    """Return today's search count for *user_id* (0 if unknown or stale date)."""
    with _lock:
        entry = _usage.get(user_id)
        if entry is None or entry["date"] != date.today():
            return 0
        return entry["count"]


def increment_usage(user_id: str) -> int:
    """Increment the search count for *user_id* and return the new count.

    Automatically resets the counter when the calendar date has changed.
    """
    today = date.today()
    with _lock:
        entry = _usage.get(user_id)
        if entry is None or entry["date"] != today:
            _usage[user_id] = {"count": 1, "date": today}
        else:
            _usage[user_id]["count"] += 1
        return _usage[user_id]["count"]


def check_limit(user_id: str) -> bool:
    """Return True if *user_id* can still perform a search (under the daily limit)."""
    return get_usage(user_id) < DAILY_LIMIT


def reset_usage(user_id: str) -> None:
    """Reset the usage counter for *user_id* (for testing / admin purposes)."""
    with _lock:
        _usage.pop(user_id, None)
