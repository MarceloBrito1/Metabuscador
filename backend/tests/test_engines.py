import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from filters import SearchResult
from engines import search_bing, search_duckduckgo, search_google, aggregate_results


def _make_mock_ctx(response_data=None, raise_http_error=False, raise_request_error=False):
    """Build a mock async context manager that mimics httpx.AsyncClient."""
    mock_response = MagicMock()
    mock_response.json.return_value = response_data or {}

    if raise_http_error:
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Server Error", request=MagicMock(), response=MagicMock()
        )
    else:
        mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    if raise_request_error:
        mock_client.get = AsyncMock(side_effect=httpx.RequestError("Connection refused"))
    else:
        mock_client.get = AsyncMock(return_value=mock_response)

    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)
    return mock_ctx


class TestSearchBing:
    async def test_returns_empty_if_api_key_none(self):
        result = await search_bing("python", api_key=None)
        assert result == []

    async def test_returns_empty_if_api_key_empty_string(self):
        result = await search_bing("python", api_key="")
        assert result == []

    async def test_returns_parsed_results_from_valid_response(self):
        data = {
            "webPages": {
                "value": [
                    {"name": "Result One", "url": "https://example.com", "snippet": "Snippet 1"},
                    {"name": "Result Two", "url": "https://other.com", "snippet": "Snippet 2"},
                ]
            }
        }
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(data)):
            results = await search_bing("python", api_key="valid_key")

        assert len(results) == 2
        assert isinstance(results[0], SearchResult)
        assert results[0].title == "Result One"
        assert results[0].url == "https://example.com"
        assert results[0].snippet == "Snippet 1"
        assert results[1].title == "Result Two"

    async def test_returns_empty_list_when_no_web_pages(self):
        data = {}
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(data)):
            results = await search_bing("python", api_key="valid_key")
        assert results == []

    async def test_raises_on_http_error(self):
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(raise_http_error=True)):
            with pytest.raises(httpx.HTTPStatusError):
                await search_bing("python", api_key="valid_key")

    async def test_raises_on_connection_error(self):
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(raise_request_error=True)):
            with pytest.raises(httpx.RequestError):
                await search_bing("python", api_key="valid_key")


class TestSearchDuckDuckGo:
    async def test_returns_empty_when_no_related_topics(self):
        data = {"RelatedTopics": []}
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(data)):
            results = await search_duckduckgo("python")
        assert results == []

    async def test_returns_parsed_results(self):
        data = {
            "RelatedTopics": [
                {
                    "FirstURL": "https://example.com/topic",
                    "Text": "A title sentence. The rest of the snippet here.",
                },
                {
                    "FirstURL": "https://other.com/topic",
                    "Text": "Another title. Another snippet.",
                },
            ]
        }
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(data)):
            results = await search_duckduckgo("python")

        assert len(results) == 2
        assert results[0].url == "https://example.com/topic"
        assert results[0].title == "A title sentence"
        assert results[0].snippet == "The rest of the snippet here."

    async def test_handles_missing_first_url(self):
        data = {
            "RelatedTopics": [
                {"Text": "Some text without a URL"},
                {"FirstURL": "https://example.com", "Text": "Valid. Entry."},
            ]
        }
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(data)):
            results = await search_duckduckgo("python")

        assert len(results) == 1
        assert results[0].url == "https://example.com"

    async def test_handles_missing_text(self):
        data = {
            "RelatedTopics": [
                {"FirstURL": "https://example.com"},  # no Text
                {"FirstURL": "https://other.com", "Text": "Valid title. Snippet."},
            ]
        }
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(data)):
            results = await search_duckduckgo("python")
        assert len(results) == 1

    async def test_handles_nested_topic_groups(self):
        data = {
            "RelatedTopics": [
                {
                    "Topics": [
                        {"FirstURL": "https://nested.com/a", "Text": "Nested A. Snippet A."},
                        {"FirstURL": "https://nested.com/b", "Text": "Nested B. Snippet B."},
                    ]
                },
                {"FirstURL": "https://top.com", "Text": "Top level. Snippet."},
            ]
        }
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(data)):
            results = await search_duckduckgo("python")

        assert len(results) == 3
        urls = [r.url for r in results]
        assert "https://nested.com/a" in urls
        assert "https://nested.com/b" in urls
        assert "https://top.com" in urls

    async def test_single_sentence_text_has_empty_snippet(self):
        data = {
            "RelatedTopics": [
                {"FirstURL": "https://example.com", "Text": "Just a title with no period separator"},
            ]
        }
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(data)):
            results = await search_duckduckgo("python")
        assert len(results) == 1
        assert results[0].snippet == ""

    async def test_raises_on_http_error(self):
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(raise_http_error=True)):
            with pytest.raises(httpx.HTTPStatusError):
                await search_duckduckgo("python")

    async def test_raises_on_connection_error(self):
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(raise_request_error=True)):
            with pytest.raises(httpx.RequestError):
                await search_duckduckgo("python")


class TestSearchGoogle:
    async def test_returns_empty_if_api_key_none(self):
        result = await search_google("python", api_key=None, cx="cx123")
        assert result == []

    async def test_returns_empty_if_cx_none(self):
        result = await search_google("python", api_key="key123", cx=None)
        assert result == []

    async def test_returns_empty_if_both_none(self):
        result = await search_google("python", api_key=None, cx=None)
        assert result == []

    async def test_returns_empty_if_api_key_empty(self):
        result = await search_google("python", api_key="", cx="cx123")
        assert result == []

    async def test_returns_empty_if_cx_empty(self):
        result = await search_google("python", api_key="key123", cx="")
        assert result == []

    async def test_returns_parsed_results(self):
        data = {
            "items": [
                {"title": "Google Result 1", "link": "https://example.com", "snippet": "Snippet 1"},
                {"title": "Google Result 2", "link": "https://other.com", "snippet": "Snippet 2"},
            ]
        }
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(data)):
            results = await search_google("python", api_key="key", cx="cx")

        assert len(results) == 2
        assert results[0].title == "Google Result 1"
        assert results[0].url == "https://example.com"
        assert results[1].snippet == "Snippet 2"

    async def test_returns_empty_when_no_items(self):
        data = {}
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(data)):
            results = await search_google("python", api_key="key", cx="cx")
        assert results == []

    async def test_raises_on_http_error(self):
        with patch("engines.httpx.AsyncClient", return_value=_make_mock_ctx(raise_http_error=True)):
            with pytest.raises(httpx.HTTPStatusError):
                await search_google("python", api_key="key", cx="cx")


class TestAggregateResults:
    async def test_combines_results_from_all_engines(self):
        bing_results = [SearchResult(title="Bing", url="https://bing.com", snippet="B")]
        ddg_results = [SearchResult(title="DDG", url="https://ddg.com", snippet="D")]
        google_results = [SearchResult(title="Google", url="https://google.com", snippet="G")]

        with (
            patch("engines.search_bing", return_value=bing_results),
            patch("engines.search_duckduckgo", return_value=ddg_results),
            patch("engines.search_google", return_value=google_results),
        ):
            results = await aggregate_results("python")

        assert len(results) == 3
        titles = [r.title for r in results]
        assert "Bing" in titles
        assert "DDG" in titles
        assert "Google" in titles

    async def test_works_when_bing_returns_empty(self):
        ddg_results = [SearchResult(title="DDG", url="https://ddg.com", snippet="D")]
        google_results = [SearchResult(title="Google", url="https://google.com", snippet="G")]

        with (
            patch("engines.search_bing", return_value=[]),
            patch("engines.search_duckduckgo", return_value=ddg_results),
            patch("engines.search_google", return_value=google_results),
        ):
            results = await aggregate_results("python")

        assert len(results) == 2

    async def test_handles_one_engine_raising_exception(self):
        ddg_results = [SearchResult(title="DDG", url="https://ddg.com", snippet="D")]
        google_results = [SearchResult(title="Google", url="https://google.com", snippet="G")]

        with (
            patch("engines.search_bing", side_effect=httpx.RequestError("Bing down")),
            patch("engines.search_duckduckgo", return_value=ddg_results),
            patch("engines.search_google", return_value=google_results),
        ):
            results = await aggregate_results("python")

        # Exception from Bing is caught; DDG and Google results still returned
        assert len(results) == 2
        titles = [r.title for r in results]
        assert "DDG" in titles
        assert "Google" in titles

    async def test_handles_all_engines_failing(self):
        with (
            patch("engines.search_bing", side_effect=httpx.RequestError("down")),
            patch("engines.search_duckduckgo", side_effect=httpx.RequestError("down")),
            patch("engines.search_google", side_effect=httpx.RequestError("down")),
        ):
            results = await aggregate_results("python")

        assert results == []

    async def test_no_api_keys_skips_bing_and_google(self):
        ddg_results = [SearchResult(title="DDG", url="https://ddg.com", snippet="D")]

        with patch("engines.search_duckduckgo", return_value=ddg_results):
            # No keys means search_bing and search_google return [] immediately
            results = await aggregate_results("python", bing_key=None, google_key=None, google_cx=None)

        assert len(results) == 1
        assert results[0].title == "DDG"
