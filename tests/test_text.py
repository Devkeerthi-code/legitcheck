from legitcheck.text import clean_text, combine_fields, dedupe_key, normalise_contacts


def test_clean_text_lowercases_and_strips_html():
    assert clean_text("<p>Hello&nbsp;<b>World</b></p>") == "hello world"


def test_clean_text_handles_missing():
    assert clean_text(None) == ""
    assert clean_text("") == ""


def test_dataset_placeholders_become_tokens():
    text = "Mail #EMAIL_0b13a2cfd4718ce252c09b2353d692a73bd32552e922c5db6cad5fb7e9a2c6c3# now"
    assert clean_text(text) == "mail emailtoken now"


def test_real_contacts_map_to_the_same_tokens():
    out = normalise_contacts("write to hr@corp.in or visit https://corp.in/jobs, call 9876543210")
    assert "emailtoken" in out and "urltoken" in out and "phonetoken" in out
    assert "hr@corp.in" not in out


def test_combine_fields_skips_blank_and_non_string_fields():
    record = {
        "title": "Intern",
        "company_profile": float("nan"),
        "description": "  ",
        "benefits": "Pay",
    }
    assert combine_fields(record) == "intern \n pay"


def test_dedupe_key_ignores_spacing_and_punctuation():
    assert dedupe_key("Data Entry, work from home!") == dedupe_key("data entry work   from home")
    assert dedupe_key("data entry") != dedupe_key("data analyst")
