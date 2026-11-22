from legitcheck import text


def test_clean_text_handles_none():
    assert text.clean_text(None) == ""


def test_clean_text_collapses_whitespace():
    assert text.clean_text("  a\n\n b  ") == "a b"


def test_dedupe_key_ignores_case_and_punctuation():
    assert text.dedupe_key("Hello  World!") == text.dedupe_key("hello world")
