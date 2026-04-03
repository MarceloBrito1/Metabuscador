import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app, aggregator
from app.models import SearchResult


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Metabuscador API"
    assert "version" in data


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_search_missing_query():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/search")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_empty_query():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/search?q=")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_with_mock(monkeypatch):
    async def mock_search(query: str, max_results_per_engine: int = 5):
        return [
            SearchResult(
                title="Python programming",
                url="https://example.com/python",
                snippet="Python is a programming language.",
                source="DuckDuckGo",
            )
        ]

    monkeypatch.setattr(aggregator, "search", mock_search)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/search?q=python")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "python"
    assert data["total"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "Python programming"
    assert data["results"][0]["source"] == "DuckDuckGo"


@pytest.mark.asyncio
async def test_search_max_results_validation(monkeypatch):
    async def mock_search(query: str, max_results_per_engine: int = 5):
        return []

    monkeypatch.setattr(aggregator, "search", mock_search)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Too high
        r1 = await client.get("/search?q=test&max_results=99")
        # Too low
        r2 = await client.get("/search?q=test&max_results=0")
    assert r1.status_code == 422
    assert r2.status_code == 422


@pytest.mark.asyncio
async def test_search_multiple_results(monkeypatch):
    mock_results = [
        SearchResult(
            title=f"Result {i}",
            url=f"https://example.com/{i}",
            snippet=f"Snippet {i}",
            source="DuckDuckGo" if i % 2 == 0 else "Wikipedia",
        )
        for i in range(6)
    ]

    async def mock_search(query: str, max_results_per_engine: int = 5):
        return mock_results

    monkeypatch.setattr(aggregator, "search", mock_search)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/search?q=python&max_results=3")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 6
    assert len(data["results"]) == 6
