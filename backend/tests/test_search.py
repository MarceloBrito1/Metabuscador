import pytest
from unittest.mock import patch
from app.schemas import SearchResult

MOCK_RESULTS = [
    SearchResult(title="Result 1", url="https://example.com/1", snippet="Snippet 1", source="DuckDuckGo"),
    SearchResult(title="Result 2", url="https://example.com/2", snippet="Snippet 2", source="DuckDuckGo"),
]

def _get_token(client, username="searcher", email="searcher@example.com", password="password123"):
    client.post("/api/auth/register", json={"username": username, "email": email, "password": password})
    resp = client.post("/api/auth/token", data={"username": username, "password": password})
    return resp.json()["access_token"]

def test_search_requires_auth(client):
    resp = client.get("/api/search/?q=python")
    assert resp.status_code == 401

def test_search_returns_results(client):
    token = _get_token(client, "s1", "s1@example.com")
    with patch("app.routers.search.aggregate_search", return_value=MOCK_RESULTS):
        resp = client.get("/api/search/?q=python", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "python"
    assert data["page"] == 1
    assert len(data["results"]) == 2
    assert data["searches_today"] == 1
    assert data["searches_remaining"] >= 0

def test_search_pagination(client):
    token = _get_token(client, "s2", "s2@example.com")
    with patch("app.routers.search.aggregate_search", return_value=MOCK_RESULTS):
        resp = client.get("/api/search/?q=python&page=2&per_page=5", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 2
    assert data["per_page"] == 5

def test_search_daily_limit(client):
    from app.config import settings
    original = settings.daily_search_limit
    settings.daily_search_limit = 2
    token = _get_token(client, "s3", "s3@example.com")
    with patch("app.routers.search.aggregate_search", return_value=MOCK_RESULTS):
        for _ in range(2):
            client.get("/api/search/?q=test", headers={"Authorization": f"Bearer {token}"})
        resp = client.get("/api/search/?q=test", headers={"Authorization": f"Bearer {token}"})
    settings.daily_search_limit = original
    assert resp.status_code == 429

def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
