import math

import pandas as pd

from legitcheck.features import (
    STRUCTURED_FEATURES,
    TEXT_FEATURES,
    parse_salary_range,
    structured_features,
    text_features,
)
from legitcheck.model.data import dedupe, split


def test_text_features_have_every_declared_name():
    assert set(text_features("hello")) == set(TEXT_FEATURES)


def test_text_features_detect_fee_and_messaging():
    f = text_features("Pay the registration fee of Rs 500. Contact HR on Telegram now!")
    assert f["fee_mentions"] >= 1
    assert f["messaging_mentions"] >= 1
    assert f["exclaim_per_100w"] > 0


def test_text_features_on_empty_text():
    f = text_features("")
    assert f["log_chars"] == 0 and f["caps_ratio"] == 0 and f["fee_mentions"] == 0


def test_caps_ratio():
    assert math.isclose(text_features("ABcd")["caps_ratio"], 0.5)


def test_unrealistic_pay_feature():
    assert text_features("Earn Rs 5,000 per day from home")["unrealistic_pay"] == 1
    assert text_features("Stipend Rs 15,000 per month")["unrealistic_pay"] == 0


def test_parse_salary_range():
    assert parse_salary_range("35000-40000") == (35000, 40000)
    assert parse_salary_range("Oct-15") is None
    assert parse_salary_range(None) is None
    assert parse_salary_range(float("nan")) is None


def test_structured_features():
    record = {
        "company_profile": None,
        "has_company_logo": 0,
        "salary_range": "0-0",
        "location": "IN",
    }
    f = structured_features(record)
    assert set(f) == set(STRUCTURED_FEATURES)
    assert f["missing_company_profile"] == 1 and f["has_company_logo"] == 0
    assert f["salary_zero_or_inverted"] == 1 and f["missing_location"] == 0


def _frame(n_real: int, n_fake: int) -> pd.DataFrame:
    rows = [{"job_id": i, "text": f"real posting {i}", "fraudulent": 0} for i in range(n_real)]
    rows += [
        {"job_id": 1000 + i, "text": f"fake posting {i}", "fraudulent": 1} for i in range(n_fake)
    ]
    df = pd.DataFrame(rows)
    df["key"] = df["text"]
    return df


def test_dedupe_marks_conflicting_copies_as_fake():
    df = pd.DataFrame(
        {
            "job_id": [1, 2, 3],
            "text": ["a", "a", "b"],
            "key": ["a", "a", "b"],
            "fraudulent": [0, 1, 0],
        }
    )
    out, report = dedupe(df)
    assert len(out) == 2 and report.conflicting_groups == 1
    assert out.set_index("key").loc["a", "fraudulent"] == 1


def test_split_is_stratified_disjoint_and_reproducible():
    df = _frame(950, 50)
    a, b = split(df), split(df)
    assert a.test["job_id"].tolist() == b.test["job_id"].tolist()
    ids = [set(p["job_id"]) for p in (a.train, a.val, a.test)]
    assert not (ids[0] & ids[1] or ids[0] & ids[2] or ids[1] & ids[2])
    for part in (a.train, a.val, a.test):
        assert abs(part["fraudulent"].mean() - 0.05) < 0.01
