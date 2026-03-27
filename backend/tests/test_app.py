import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport

import usage
from usage import DAILY_LIMIT, reset_usage
from filters import SearchResult
from app import app


@pytest.fixture(autouse=True)
def reset_test_user():
    """Reset usage for all test user IDs used in this module."""
    users = ["anonymous", "user1", "rate_limited_user", "test_profile_user"]
    for u in users:
        reset_usage(u)
    yield
    for u in users:
        reset_usage(u)


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# GET /usage/{user_id}
# ---------------------------------------------------------------------------

class TestUsageEndpoint:
    async def test_returns_200_with_correct_structure(self, client):
        response = await client.get("/usage/user1")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "count" in data
        assert "limit" in data
        assert "remaining" in data

    async def test_new_user_has_zero_count(self, client):
        response = await client.get("/usage/user1")
        data = response.json()
        assert data["user_id"] == "user1"
        assert data["count"] == 0
        assert data["limit"] == 100
        assert data["remaining"] == 100

    async def test_after_searches_count_reflects_usage(self, client):
        # Directly increment usage to simulate prior searches
        from usage import increment_usage
        increment_usage("user1")
        increment_usage("user1")
        increment_usage("user1")

        response = await client.get("/usage/user1")
        data = response.json()
        assert data["count"] == 3
        assert data["remaining"] == 97


# ---------------------------------------------------------------------------
# GET /search
# ---------------------------------------------------------------------------

class TestSearchEndpointValidation:
    async def test_missing_q_returns_422(self, client):
        response = await client.get("/search")
        assert response.status_code == 422

    async def test_unknown_profile_returns_422(self, client):
        response = await client.get("/search?q=python&profile=invalid_profile")
        assert response.status_code == 422


class TestSearchEndpointRateLimit:
    async def test_returns_429_when_limit_exceeded(self, client):
        with patch("app.check_limit", return_value=False):
            response = await client.get("/search?q=python&user_id=rate_limited_user")
        assert response.status_code == 429
        data = response.json()
        assert "Daily search limit reached" in data["detail"]["error"]
        assert data["detail"]["limit"] == DAILY_LIMIT


class TestSearchEndpointSuccess:
    def _make_results(self):
        return [
            SearchResult(title="Result One", url="https://example.com", snippet="Snippet 1"),
            SearchResult(title="Result Two", url="https://other.com", snippet="Snippet 2"),
        ]

    async def test_returns_200_with_correct_structure(self, client):
        with patch("app.aggregate_results", return_value=self._make_results()):
            response = await client.get("/search?q=python&user_id=user1")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "profile" in data
        assert "count" in data
        assert "remaining" in data

    async def test_results_have_expected_fields(self, client):
        with patch("app.aggregate_results", return_value=self._make_results()):
            response = await client.get("/search?q=python&user_id=user1")
        data = response.json()
        for result in data["results"]:
            assert "title" in result
            assert "url" in result
            assert "snippet" in result

    async def test_default_profile_is_general(self, client):
        with patch("app.aggregate_results", return_value=self._make_results()):
            response = await client.get("/search?q=python&user_id=user1")
        data = response.json()
        assert data["profile"] == "general"

    async def test_scientific_profile_accepted(self, client):
        with patch("app.aggregate_results", return_value=self._make_results()):
            response = await client.get("/search?q=python&profile=scientific&user_id=user1")
        assert response.status_code == 200
        assert response.json()["profile"] == "scientific"

    async def test_journalistic_profile_accepted(self, client):
        with patch("app.aggregate_results", return_value=self._make_results()):
            response = await client.get("/search?q=python&profile=journalistic&user_id=user1")
        assert response.status_code == 200
        assert response.json()["profile"] == "journalistic"

    async def test_shopping_profile_accepted(self, client):
        with patch("app.aggregate_results", return_value=self._make_results()):
            response = await client.get("/search?q=python&profile=shopping&user_id=user1")
        assert response.status_code == 200
        assert response.json()["profile"] == "shopping"

    async def test_user_id_defaults_to_anonymous(self, client):
        with patch("app.aggregate_results", return_value=self._make_results()):
            response = await client.get("/search?q=python")
        assert response.status_code == 200
        # Check anonymous usage incremented
        from usage import get_usage
        assert get_usage("anonymous") >= 1

    async def test_count_and_remaining_are_correct(self, client):
        with patch("app.aggregate_results", return_value=self._make_results()):
            response = await client.get("/search?q=python&user_id=user1")
        data = response.json()
        assert data["count"] == 1
        assert data["remaining"] == DAILY_LIMIT - 1

    async def test_filters_applied_ads_removed(self, client):
        raw = [
            SearchResult(title="Ad", url="https://doubleclick.net/ad", snippet="S", is_ad=True),
            SearchResult(title="Normal", url="https://example.com", snippet="S"),
        ]
        with patch("app.aggregate_results", return_value=raw):
            response = await client.get("/search?q=python&user_id=user1")
        data = response.json()
        urls = [r["url"] for r in data["results"]]
        assert "https://doubleclick.net/ad" not in urls
        assert "https://example.com" in urls

    async def test_filters_applied_duplicates_removed(self, client):
        raw = [
            SearchResult(title="First", url="https://example.com", snippet="S1"),
            SearchResult(title="Second", url="https://example.com", snippet="S2"),
            SearchResult(title="Other", url="https://other.com", snippet="S3"),
        ]
        with patch("app.aggregate_results", return_value=raw):
            response = await client.get("/search?q=python&user_id=user1")
        data = response.json()
        urls = [r["url"] for r in data["results"]]
        assert urls.count("https://example.com") == 1

    async def test_scientific_profile_sorts_edu_to_top(self, client):
        raw = [
            SearchResult(title="ComResult", url="https://example.com", snippet="S"),
            SearchResult(title="EduResult", url="https://university.edu/paper", snippet="S"),
        ]
        with patch("app.aggregate_results", return_value=raw):
            response = await client.get("/search?q=python&profile=scientific&user_id=user1")
        data = response.json()
        assert data["results"][0]["title"] == "EduResult"

    async def test_empty_results_from_engines(self, client):
        with patch("app.aggregate_results", return_value=[]):
            response = await client.get("/search?q=python&user_id=user1")
        assert response.status_code == 200
        assert response.json()["results"] == []
