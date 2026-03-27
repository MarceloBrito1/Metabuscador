import pytest
from filters import SearchResult, remove_duplicates, remove_ads, clean_results, KNOWN_AD_DOMAINS


class TestSearchResult:
    def test_creation_with_all_fields(self):
        r = SearchResult(title="Test", url="https://example.com", snippet="A snippet", is_ad=True)
        assert r.title == "Test"
        assert r.url == "https://example.com"
        assert r.snippet == "A snippet"
        assert r.is_ad is True

    def test_default_is_ad_is_false(self):
        r = SearchResult(title="Test", url="https://example.com", snippet="A snippet")
        assert r.is_ad is False

    def test_equality(self):
        r1 = SearchResult(title="Test", url="https://example.com", snippet="A snippet")
        r2 = SearchResult(title="Test", url="https://example.com", snippet="A snippet")
        assert r1 == r2

    def test_inequality_different_title(self):
        r1 = SearchResult(title="Test", url="https://example.com", snippet="A snippet")
        r2 = SearchResult(title="Other", url="https://example.com", snippet="A snippet")
        assert r1 != r2

    def test_inequality_different_url(self):
        r1 = SearchResult(title="Test", url="https://example.com", snippet="S")
        r2 = SearchResult(title="Test", url="https://other.com", snippet="S")
        assert r1 != r2

    def test_is_ad_affects_equality(self):
        r1 = SearchResult(title="T", url="https://example.com", snippet="S", is_ad=True)
        r2 = SearchResult(title="T", url="https://example.com", snippet="S", is_ad=False)
        assert r1 != r2


class TestRemoveDuplicates:
    def test_empty_list_returns_empty(self):
        assert remove_duplicates([]) == []

    def test_single_result_unchanged(self):
        r = SearchResult(title="T", url="https://example.com", snippet="S")
        assert remove_duplicates([r]) == [r]

    def test_exact_url_duplicates_removed(self):
        r1 = SearchResult(title="First", url="https://example.com", snippet="S1")
        r2 = SearchResult(title="Second", url="https://example.com", snippet="S2")
        result = remove_duplicates([r1, r2])
        assert result == [r1]
        assert len(result) == 1

    def test_www_vs_without_treated_as_duplicate(self):
        r1 = SearchResult(title="T1", url="https://example.com/page", snippet="S1")
        r2 = SearchResult(title="T2", url="https://www.example.com/page", snippet="S2")
        result = remove_duplicates([r1, r2])
        assert len(result) == 1
        assert result[0] == r1

    def test_trailing_slash_vs_without_treated_as_duplicate(self):
        r1 = SearchResult(title="T1", url="https://example.com/page", snippet="S1")
        r2 = SearchResult(title="T2", url="https://example.com/page/", snippet="S2")
        result = remove_duplicates([r1, r2])
        assert len(result) == 1

    def test_case_insensitive_url_comparison(self):
        r1 = SearchResult(title="T1", url="https://example.com/page", snippet="S1")
        r2 = SearchResult(title="T2", url="HTTPS://EXAMPLE.COM/PAGE", snippet="S2")
        result = remove_duplicates([r1, r2])
        assert len(result) == 1

    def test_different_urls_all_kept(self):
        r1 = SearchResult(title="T1", url="https://example.com", snippet="S1")
        r2 = SearchResult(title="T2", url="https://other.com", snippet="S2")
        r3 = SearchResult(title="T3", url="https://third.com", snippet="S3")
        result = remove_duplicates([r1, r2, r3])
        assert len(result) == 3

    def test_preserves_first_occurrence(self):
        r1 = SearchResult(title="First", url="https://example.com", snippet="S1")
        r2 = SearchResult(title="Second", url="https://example.com", snippet="S2")
        result = remove_duplicates([r1, r2])
        assert result[0].title == "First"

    def test_multiple_duplicates_all_collapsed(self):
        r1 = SearchResult(title="First", url="https://example.com", snippet="S1")
        r2 = SearchResult(title="Second", url="https://example.com", snippet="S2")
        r3 = SearchResult(title="Third", url="https://example.com", snippet="S3")
        result = remove_duplicates([r1, r2, r3])
        assert len(result) == 1
        assert result[0].title == "First"

    def test_query_string_preserved_in_dedup(self):
        r1 = SearchResult(title="T1", url="https://example.com/page?q=1", snippet="S1")
        r2 = SearchResult(title="T2", url="https://example.com/page?q=2", snippet="S2")
        # Different query strings → different URLs
        result = remove_duplicates([r1, r2])
        assert len(result) == 2


class TestRemoveAds:
    def test_empty_list_returns_empty(self):
        assert remove_ads([]) == []

    def test_is_ad_true_removed(self):
        r = SearchResult(title="Ad", url="https://example.com", snippet="S", is_ad=True)
        assert remove_ads([r]) == []

    def test_is_ad_false_kept(self):
        r = SearchResult(title="Normal", url="https://example.com", snippet="S", is_ad=False)
        assert remove_ads([r]) == [r]

    def test_known_ad_domain_doubleclick_removed(self):
        r = SearchResult(title="Ad", url="https://doubleclick.net/ad?id=123", snippet="S")
        assert remove_ads([r]) == []

    def test_known_ad_domain_taboola_removed(self):
        r = SearchResult(title="Ad", url="https://taboola.com/sponsored", snippet="S")
        assert remove_ads([r]) == []

    def test_normal_result_kept(self):
        r = SearchResult(title="Normal", url="https://example.com/article", snippet="S")
        assert remove_ads([r]) == [r]

    def test_mixed_ad_and_normal_only_normal_kept(self):
        ad = SearchResult(title="Ad", url="https://doubleclick.net/ad", snippet="S", is_ad=True)
        normal = SearchResult(title="Normal", url="https://example.com", snippet="S")
        result = remove_ads([ad, normal])
        assert result == [normal]

    def test_is_ad_flag_beats_normal_domain(self):
        # Even a non-ad-domain URL is removed when is_ad=True
        r = SearchResult(title="Ad", url="https://example.com", snippet="S", is_ad=True)
        assert remove_ads([r]) == []

    def test_ad_domain_without_is_ad_flag_still_removed(self):
        r = SearchResult(title="T", url="https://outbrain.com/something", snippet="S", is_ad=False)
        assert remove_ads([r]) == []


class TestCleanResults:
    def test_empty_list_returns_empty(self):
        assert clean_results([]) == []

    def test_ads_removed(self):
        ad = SearchResult(title="Ad", url="https://doubleclick.net/ad", snippet="S", is_ad=True)
        result = clean_results([ad])
        assert result == []

    def test_duplicates_removed(self):
        r1 = SearchResult(title="First", url="https://example.com", snippet="S1")
        r2 = SearchResult(title="Second", url="https://example.com", snippet="S2")
        result = clean_results([r1, r2])
        assert result == [r1]

    def test_combines_both_filters(self):
        ad = SearchResult(title="Ad", url="https://doubleclick.net/ad", snippet="S", is_ad=True)
        dup1 = SearchResult(title="Dup1", url="https://example.com", snippet="S1")
        dup2 = SearchResult(title="Dup2", url="https://example.com", snippet="S2")
        normal = SearchResult(title="Normal", url="https://other.com", snippet="S")
        result = clean_results([ad, dup1, dup2, normal])
        assert len(result) == 2
        assert ad not in result
        assert dup2 not in result
        assert dup1 in result
        assert normal in result

    def test_ads_removed_before_dedup(self):
        # An ad and a normal result with the same URL:
        # remove_ads removes the ad first, leaving the normal result.
        ad = SearchResult(title="Ad", url="https://example.com", snippet="S", is_ad=True)
        normal = SearchResult(title="Normal", url="https://example.com", snippet="S")
        # After remove_ads → [normal]; after remove_duplicates → [normal]
        result = clean_results([ad, normal])
        assert result == [normal]

    def test_normal_results_unchanged(self):
        r1 = SearchResult(title="T1", url="https://example.com", snippet="S1")
        r2 = SearchResult(title="T2", url="https://other.com", snippet="S2")
        result = clean_results([r1, r2])
        assert result == [r1, r2]
