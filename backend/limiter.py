"""Daily search-limit tracker (in-memory, resets at midnight UTC)."""

from __future__ import annotations

import os
from datetime import date
from typing import Dict, Tuple

DAILY_LIMIT: int = int(os.getenv("DAILY_LIMIT", "100"))

# { user_id: (date, count) }
_counters: Dict[str, Tuple[date, int]] = {}


def _today() -> date:
    return date.today()


def get_remaining(user_id: str) -> int:
    """Return how many searches the user can still perform today."""
    today = _today()
    entry = _counters.get(user_id)
    if entry is None or entry[0] != today:
        return DAILY_LIMIT
    return max(0, DAILY_LIMIT - entry[1])


def consume(user_id: str) -> bool:
    """
    Register one search for *user_id*.

    Returns True if the search is allowed (limit not exceeded),
    False otherwise.
    """
    today = _today()
    entry = _counters.get(user_id)
    if entry is None or entry[0] != today:
        _counters[user_id] = (today, 1)
        return True
    current_count = entry[1]
    if current_count >= DAILY_LIMIT:
        return False
    _counters[user_id] = (today, current_count + 1)
    return True
