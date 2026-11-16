"""The saved model must reproduce the numbers reported in models/metrics.json.

The full check needs the Kaggle CSV (not in git), so CI skips it; the synthetic-score
fingerprint needs only the committed files and always runs.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from legitcheck.model import data as D
from legitcheck.model.metrics import as_dict, at_threshold, score
from legitcheck.model.synthetic import load_synthetic

METRICS = json.loads(
    (Path(__file__).resolve().parents[1] / "models" / "metrics.json").read_text(encoding="utf-8")
)


def test_saved_model_reproduces_synthetic_scores(model):
    records = load_synthetic()
    scores = model.score_texts([r["text"] for r in records])
    expected = METRICS["synthetic_india"]["model_scores"]
    for record, value in zip(records, scores, strict=True):
        assert value == pytest.approx(expected[record["id"]], abs=1e-6)


def test_thresholds_match_report(model):
    assert model.warn_threshold == pytest.approx(METRICS["thresholds"]["warn"], abs=1e-6)
    assert model.high_threshold == pytest.approx(METRICS["thresholds"]["high"], abs=1e-6)


def _dataset_available() -> bool:
    try:
        D.find_dataset()
        return True
    except FileNotFoundError:
        return False


@pytest.mark.skipif(not _dataset_available(), reason="Kaggle CSV not present (see README > Data)")
def test_saved_model_reproduces_test_metrics(model):
    path = D.find_dataset()
    assert D.file_sha256(path) == METRICS["dataset"]["file_sha256"]
    df, _ = D.dedupe(D.load_postings(path))
    test = D.split(df).test
    assert D.ids_fingerprint(test) == METRICS["dataset"]["test_ids_fingerprint"]

    y = test["fraudulent"].to_numpy()
    p = model.score_texts(test["raw_text"].tolist(), test["text"].tolist())
    reported = METRICS["test"][METRICS["chosen_model"]]
    for key, value in as_dict(score(y, p)).items():
        assert value == pytest.approx(reported[key], abs=1e-6), key
    for name in ("warn", "high"):
        got = as_dict(at_threshold(y, p, getattr(model, f"{name}_threshold")))
        want = METRICS["test_chosen_at_thresholds"][name]
        assert {k: got[k] for k in ("tp", "fp", "fn", "tn")} == {
            k: want[k] for k in ("tp", "fp", "fn", "tn")
        }
    assert np.isfinite(p).all()
