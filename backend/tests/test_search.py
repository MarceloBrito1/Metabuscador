import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models import SearchResult
from app.search.aggregator import SearchAggregator
from app.search.wikipedia import WikipediaSearcher
from app.search.duckduckgo import DuckDuckGoSearcher


# ---------------------------------------------------------------------------
# Wikipedia searcher tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_wikipedia_search_success():
    searcher = WikipediaSearcher()
    mock_data = {
        "query": {
            "search": [
                {
                    "title": "Python (programming language)",
                    "snippet": 'Python is a <span class="searchmatch">high-level</span> language.',
                }
            ]
        }
    }
    mock_response = MagicMock()
    mock_response.json.return_value = mock_data
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        results = await searcher.search("python")

    assert len(results) == 1
    assert results[0].source == "Wikipedia"
    assert results[0].title == "Python (programming language)"
    assert results[0].url == "https://en.wikipedia.org/wiki/Python_(programming_language)"
    # HTML tags should be stripped from snippet
    assert "<span" not in results[0].snippet


@pytest.mark.asyncio
async def test_wikipedia_search_http_error():
    searcher = WikipediaSearcher()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("Network error"))
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        results = await searcher.search("python")

    assert results == []


@pytest.mark.asyncio
async def test_wikipedia_search_empty_response():
    searcher = WikipediaSearcher()
    mock_response = MagicMock()
    mock_response.json.return_value = {"query": {"search": []}}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        results = await searcher.search("xyzzy123notarealquery")

    assert results == []


# ---------------------------------------------------------------------------
# DuckDuckGo searcher tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_duckduckgo_search_success():
    searcher = DuckDuckGoSearcher()
    mock_raw = [
        {"title": "DDG Result", "href": "https://ddg.com/result", "body": "A result."}
    ]

    with patch.object(searcher, "_fetch", return_value=[
        SearchResult(
            title="DDG Result",
            url="https://ddg.com/result",
            snippet="A result.",
            source="DuckDuckGo",
        )
    ]):
        results = await searcher.search("test")

    assert len(results) == 1
    assert results[0].source == "DuckDuckGo"
    assert results[0].title == "DDG Result"


@pytest.mark.asyncio
async def test_duckduckgo_search_error():
    searcher = DuckDuckGoSearcher()

    with patch.object(searcher, "_fetch", side_effect=Exception("Rate limited")):
        results = await searcher.search("test")

    assert results == []


# ---------------------------------------------------------------------------
# Aggregator tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_aggregator_combines_results():
    result_a = SearchResult(
        title="A", url="https://a.com", snippet="A snippet", source="EngineA"
    )
    result_b = SearchResult(
        title="B", url="https://b.com", snippet="B snippet", source="EngineB"
    )

    searcher1 = AsyncMock()
    searcher1.search = AsyncMock(return_value=[result_a])
    searcher2 = AsyncMock()
    searcher2.search = AsyncMock(return_value=[result_b])

    agg = SearchAggregator([searcher1, searcher2])
    results = await agg.search("query")

    urls = {r.url for r in results}
    assert urls == {"https://a.com", "https://b.com"}


@pytest.mark.asyncio
async def test_aggregator_deduplication():
    result1 = SearchResult(
        title="Dup", url="https://same.com", snippet="s1", source="A"
    )
    result2 = SearchResult(
        title="Dup2", url="https://same.com", snippet="s2", source="B"
    )
    result3 = SearchResult(
        title="Unique", url="https://unique.com", snippet="s3", source="A"
    )

    searcher1 = AsyncMock()
    searcher1.search = AsyncMock(return_value=[result1, result3])
    searcher2 = AsyncMock()
    searcher2.search = AsyncMock(return_value=[result2])

    agg = SearchAggregator([searcher1, searcher2])
    results = await agg.search("test")

    urls = {r.url for r in results}
    assert len(urls) == 2, "Duplicate URLs found"
    assert urls == {"https://same.com", "https://unique.com"}


@pytest.mark.asyncio
async def test_aggregator_handles_engine_exception():
    result = SearchResult(
        title="OK", url="https://ok.com", snippet="ok", source="B"
    )

    searcher1 = AsyncMock()
    searcher1.search = AsyncMock(side_effect=Exception("Timeout"))
    searcher2 = AsyncMock()
    searcher2.search = AsyncMock(return_value=[result])

    agg = SearchAggregator([searcher1, searcher2])
    results = await agg.search("test")

    assert len(results) == 1
    assert results[0].url == "https://ok.com"


@pytest.mark.asyncio
async def test_aggregator_empty_results():
    searcher1 = AsyncMock()
    searcher1.search = AsyncMock(return_value=[])
    searcher2 = AsyncMock()
    searcher2.search = AsyncMock(return_value=[])

    agg = SearchAggregator([searcher1, searcher2])
    results = await agg.search("obscurequery")

    assert results == []


@pytest.mark.asyncio
async def test_aggregator_skips_empty_url():
    result_no_url = SearchResult(
        title="No URL", url="", snippet="s", source="A"
    )
    result_valid = SearchResult(
        title="Valid", url="https://valid.com", snippet="s", source="A"
    )

    searcher = AsyncMock()
    searcher.search = AsyncMock(return_value=[result_no_url, result_valid])

    agg = SearchAggregator([searcher])
    results = await agg.search("test")

    assert len(results) == 1
    assert results[0].url == "https://valid.com"
