from legitcheck import text


def test_clean_text_handles_none():
    assert text.clean_text(None) == ""
