from legitcheck.rules import links


def test_levenshtein_classic_pair():
    assert links.levenshtein("kitten", "sitting") == 3


def test_levenshtein_identical_and_empty():
    assert links.levenshtein("abc", "abc") == 0
    assert links.levenshtein("", "") == 0
    assert links.levenshtein("a", "") == 1


def test_levenshtein_is_symmetric():
    assert links.levenshtein("flaw", "lawn") == links.levenshtein("lawn", "flaw") == 2


def test_registered_domain_strips_subdomain():
    assert links.registered_domain("jobs.infosys.com") == "infosys.com"


def test_registered_domain_keeps_two_part_suffix():
    assert links.registered_domain("a.b.co.in") == "b.co.in"


def test_registered_domain_leaves_bare_domain():
    assert links.registered_domain("tcs.com") == "tcs.com"


def test_lookalike_brand_flags_hyphenated_brand():
    assert links.lookalike_brand("tcs-hiring.in") == "tcs"


def test_lookalike_brand_flags_brand_on_odd_tld():
    assert links.lookalike_brand("amazon-jobs.xyz") == "amazon"


def test_lookalike_brand_ignores_official_domain():
    assert links.lookalike_brand("wipro.com") is None
