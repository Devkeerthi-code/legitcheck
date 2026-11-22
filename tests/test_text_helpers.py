from legitcheck import text


def test_clean_text_handles_none():
    assert text.clean_text(None) == ""


def test_clean_text_collapses_whitespace():
    assert text.clean_text("  a\n\n b  ") == "a b"
