from legitcheck.rules import base


def test_is_negated_detects_no_fee_statement():
    sentence = "No registration fee is charged"
    assert base.is_negated(sentence, sentence.index("registration"))
