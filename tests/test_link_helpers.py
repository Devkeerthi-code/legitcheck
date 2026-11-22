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
