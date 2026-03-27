import pytest
from datetime import date, timedelta

import usage
from usage import DAILY_LIMIT, get_usage, check_limit, increment_usage, reset_usage


@pytest.fixture(autouse=True)
def clean_user():
    """Provide a test user ID and ensure clean state before and after each test."""
    user_id = "test_user_pytest"
    reset_usage(user_id)
    yield user_id
    reset_usage(user_id)


class TestDailyLimit:
    def test_daily_limit_equals_100(self):
        assert DAILY_LIMIT == 100


class TestGetUsage:
    def test_new_user_returns_zero(self, clean_user):
        assert get_usage(clean_user) == 0

    def test_unknown_user_returns_zero(self):
        assert get_usage("completely_unknown_user_xyz") == 0

    def test_user_with_usage_returns_correct_count(self, clean_user):
        increment_usage(clean_user)
        increment_usage(clean_user)
        assert get_usage(clean_user) == 2

    def test_usage_from_yesterday_returns_zero(self, clean_user):
        yesterday = date.today() - timedelta(days=1)
        with usage._lock:
            usage._usage[clean_user] = {"count": 50, "date": yesterday}
        assert get_usage(clean_user) == 0

    def test_usage_with_future_date_returns_zero(self, clean_user):
        tomorrow = date.today() + timedelta(days=1)
        with usage._lock:
            usage._usage[clean_user] = {"count": 10, "date": tomorrow}
        assert get_usage(clean_user) == 0

    def test_usage_today_returns_count(self, clean_user):
        with usage._lock:
            usage._usage[clean_user] = {"count": 42, "date": date.today()}
        assert get_usage(clean_user) == 42


class TestCheckLimit:
    def test_new_user_can_search(self, clean_user):
        assert check_limit(clean_user) is True

    def test_user_at_limit_minus_one_can_search(self, clean_user):
        with usage._lock:
            usage._usage[clean_user] = {"count": DAILY_LIMIT - 1, "date": date.today()}
        assert check_limit(clean_user) is True

    def test_user_at_limit_cannot_search(self, clean_user):
        with usage._lock:
            usage._usage[clean_user] = {"count": DAILY_LIMIT, "date": date.today()}
        assert check_limit(clean_user) is False

    def test_user_over_limit_cannot_search(self, clean_user):
        with usage._lock:
            usage._usage[clean_user] = {"count": DAILY_LIMIT + 10, "date": date.today()}
        assert check_limit(clean_user) is False

    def test_stale_entry_allows_search(self, clean_user):
        # An entry from yesterday means today's count is 0 → under limit
        yesterday = date.today() - timedelta(days=1)
        with usage._lock:
            usage._usage[clean_user] = {"count": DAILY_LIMIT, "date": yesterday}
        assert check_limit(clean_user) is True


class TestIncrementUsage:
    def test_first_increment_returns_one(self, clean_user):
        assert increment_usage(clean_user) == 1

    def test_multiple_increments_accumulate(self, clean_user):
        increment_usage(clean_user)
        increment_usage(clean_user)
        result = increment_usage(clean_user)
        assert result == 3

    def test_returns_new_count_each_time(self, clean_user):
        r1 = increment_usage(clean_user)
        r2 = increment_usage(clean_user)
        assert r1 == 1
        assert r2 == 2

    def test_resets_to_one_when_date_has_changed(self, clean_user):
        yesterday = date.today() - timedelta(days=1)
        with usage._lock:
            usage._usage[clean_user] = {"count": 50, "date": yesterday}
        # Calling increment_usage with today's date should reset counter
        result = increment_usage(clean_user)
        assert result == 1

    def test_resets_count_stored_with_today(self, clean_user):
        yesterday = date.today() - timedelta(days=1)
        with usage._lock:
            usage._usage[clean_user] = {"count": 50, "date": yesterday}
        increment_usage(clean_user)
        # After reset, get_usage should return 1 (today's count)
        assert get_usage(clean_user) == 1

    def test_get_usage_consistent_with_increment(self, clean_user):
        for _ in range(5):
            increment_usage(clean_user)
        assert get_usage(clean_user) == 5


class TestResetUsage:
    def test_reset_clears_usage(self, clean_user):
        increment_usage(clean_user)
        increment_usage(clean_user)
        reset_usage(clean_user)
        assert get_usage(clean_user) == 0

    def test_reset_nonexistent_user_is_safe(self):
        # Should not raise
        reset_usage("nonexistent_user_abc_xyz")

    def test_reset_allows_fresh_increment(self, clean_user):
        increment_usage(clean_user)
        increment_usage(clean_user)
        reset_usage(clean_user)
        assert increment_usage(clean_user) == 1
