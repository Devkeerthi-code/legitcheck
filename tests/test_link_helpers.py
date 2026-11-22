from legitcheck.rules import links


def test_levenshtein_classic_pair():
    assert links.levenshtein("kitten", "sitting") == 3


def test_levenshtein_identical_and_empty():
    assert links.levenshtein("abc", "abc") == 0
    assert links.levenshtein("", "") == 0
    assert links.levenshtein("a", "") == 1
