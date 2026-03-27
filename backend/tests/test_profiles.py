import pytest
from filters import SearchResult
from profiles import get_domain, score_result, apply_profile, PROFILES


def make_result(url: str, title: str = "Title") -> SearchResult:
    return SearchResult(title=title, url=url, snippet="Snippet")


class TestGetDomain:
    def test_basic_url(self):
        assert get_domain("https://example.com/path") == "example.com"

    def test_www_stripped(self):
        assert get_domain("https://www.example.com") == "example.com"

    def test_subdomain_preserved(self):
        # get_domain only strips leading www., not other subdomains
        assert get_domain("https://sub.domain.example.edu") == "sub.domain.example.edu"

    def test_url_with_port(self):
        assert get_domain("https://example.com:8080") == "example.com:8080"

    def test_empty_string(self):
        assert get_domain("") == ""

    def test_url_no_path(self):
        assert get_domain("https://bbc.com") == "bbc.com"

    def test_url_with_query(self):
        assert get_domain("https://example.com/search?q=test") == "example.com"


class TestScoreResult:
    # --- scientific profile ---

    def test_scientific_edu_tld_scores_boost(self):
        r = make_result("https://university.edu/research")
        assert score_result(r, "scientific") == 10

    def test_scientific_gov_tld_scores_boost(self):
        r = make_result("https://nih.gov/study")
        assert score_result(r, "scientific") == 10

    def test_scientific_com_scores_zero(self):
        r = make_result("https://example.com/article")
        assert score_result(r, "scientific") == 0

    def test_scientific_org_scores_zero(self):
        r = make_result("https://wikipedia.org/wiki/Topic")
        assert score_result(r, "scientific") == 0

    # --- journalistic profile ---

    def test_journalistic_bbc_scores_boost(self):
        r = make_result("https://bbc.com/news/world")
        assert score_result(r, "journalistic") == 10

    def test_journalistic_reuters_scores_boost(self):
        r = make_result("https://reuters.com/article/123")
        assert score_result(r, "journalistic") == 10

    def test_journalistic_unknown_com_scores_zero(self):
        r = make_result("https://randomnewsblog.com/article")
        assert score_result(r, "journalistic") == 0

    def test_journalistic_edu_scores_zero(self):
        r = make_result("https://university.edu")
        assert score_result(r, "journalistic") == 0

    # --- shopping profile ---

    def test_shopping_amazon_scores_boost(self):
        r = make_result("https://amazon.com/dp/B000TEST")
        assert score_result(r, "shopping") == 10

    def test_shopping_ebay_scores_boost(self):
        r = make_result("https://ebay.com/itm/12345")
        assert score_result(r, "shopping") == 10

    def test_shopping_normal_site_scores_zero(self):
        r = make_result("https://example.com/product")
        assert score_result(r, "shopping") == 0

    # --- unknown profile ---

    def test_unknown_profile_returns_zero(self):
        r = make_result("https://university.edu")
        assert score_result(r, "unknown_profile") == 0

    def test_general_profile_returns_zero(self):
        # "general" is not in PROFILES dict
        r = make_result("https://bbc.com")
        assert score_result(r, "general") == 0


class TestApplyProfile:
    def test_empty_list_returns_empty(self):
        assert apply_profile([], "scientific") == []

    def test_scientific_sorts_edu_to_top(self):
        com = make_result("https://example.com", "com")
        edu = make_result("https://university.edu", "edu")
        result = apply_profile([com, edu], "scientific")
        assert result[0].title == "edu"

    def test_scientific_sorts_gov_to_top(self):
        com = make_result("https://example.com", "com")
        gov = make_result("https://agency.gov", "gov")
        result = apply_profile([com, gov], "scientific")
        assert result[0].title == "gov"

    def test_journalistic_sorts_news_to_top(self):
        other = make_result("https://randomsite.com", "other")
        bbc = make_result("https://bbc.com/news", "bbc")
        result = apply_profile([other, bbc], "journalistic")
        assert result[0].title == "bbc"

    def test_journalistic_multiple_news_sites(self):
        other = make_result("https://example.com", "other")
        bbc = make_result("https://bbc.com", "bbc")
        reuters = make_result("https://reuters.com", "reuters")
        result = apply_profile([other, bbc, reuters], "journalistic")
        # other should be last
        assert result[-1].title == "other"

    def test_shopping_sorts_shopping_to_top(self):
        other = make_result("https://example.com", "other")
        amazon = make_result("https://amazon.com/product", "amazon")
        result = apply_profile([other, amazon], "shopping")
        assert result[0].title == "amazon"

    def test_unknown_profile_returns_unchanged(self):
        r1 = make_result("https://example.com", "first")
        r2 = make_result("https://other.com", "second")
        result = apply_profile([r1, r2], "unknown_profile")
        assert result == [r1, r2]

    def test_general_profile_returns_unchanged(self):
        # "general" is not a key in PROFILES, so list is returned as-is
        r1 = make_result("https://example.com", "first")
        r2 = make_result("https://other.com", "second")
        result = apply_profile([r1, r2], "general")
        assert result == [r1, r2]

    def test_same_score_maintains_relative_order(self):
        # Both are .com, both score 0 under scientific; Python sort is stable
        r1 = make_result("https://site1.com", "first")
        r2 = make_result("https://site2.com", "second")
        result = apply_profile([r1, r2], "scientific")
        assert result[0].title == "first"
        assert result[1].title == "second"

    def test_profiles_dict_contains_expected_keys(self):
        assert "scientific" in PROFILES
        assert "journalistic" in PROFILES
        assert "shopping" in PROFILES
        assert "general" not in PROFILES

    def test_scientific_profile_boost_score_is_ten(self):
        assert PROFILES["scientific"]["boost_score"] == 10

    def test_journalistic_profile_boost_score_is_ten(self):
        assert PROFILES["journalistic"]["boost_score"] == 10

    def test_shopping_profile_boost_score_is_ten(self):
        assert PROFILES["shopping"]["boost_score"] == 10
