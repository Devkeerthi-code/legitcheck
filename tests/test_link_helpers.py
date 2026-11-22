from legitcheck.rules import links


def test_levenshtein_classic_pair():
    assert links.levenshtein("kitten", "sitting") == 3
