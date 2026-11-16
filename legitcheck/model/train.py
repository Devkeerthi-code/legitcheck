"""Train, compare, calibrate, pick thresholds on validation, then evaluate on test once.

Run: python -m legitcheck.model.train
Writes models/legitcheck.joblib, models/metrics.json and plots in reports/figures/.
"""

from __future__ import annotations

import json
import platform
from collections.abc import Callable
from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .. import __version__
from ..features import STRUCTURED_FEATURES, TEXT_FEATURES, structured_features, text_features
from . import data as D
from .metrics import (
    TARGET_PRECISION,
    TARGET_RECALL,
    as_dict,
    at_threshold,
    recall_at_precision,
    score,
    threshold_for_recall,
)
from .predictor import MODEL_PATH, LegitModel
from .report import write_figures
from .synthetic import evaluate_synthetic, load_synthetic

MODELS_DIR = MODEL_PATH.parent
C_GRID = (0.5, 2.0, 8.0, 32.0)


def make_vectorizer() -> TfidfVectorizer:
    # Word 1-2 grams keep the explanations readable ("training fee", "work from").
    return TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.9,
        max_features=60_000,
        sublinear_tf=True,
        strip_accents="unicode",
        dtype=np.float32,
    )


def calibrated(estimator: object) -> CalibratedClassifierCV:
    # Sigmoid (Platt) over 5 folds: isotonic overfits with ~600 positives.
    # ensemble=False keeps ONE base model, so its coefficients explain every prediction.
    return CalibratedClassifierCV(estimator, method="sigmoid", cv=5, ensemble=False)


def feature_matrices(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """(text-only features, text + structured features) for every row."""
    text_rows, structured_rows = [], []
    for record, raw in zip(frame.to_dict(orient="records"), frame["raw_text"], strict=True):
        tf, sf = text_features(raw), structured_features(record)
        text_rows.append([tf[n] for n in TEXT_FEATURES])
        structured_rows.append([sf[n] for n in STRUCTURED_FEATURES])
    text_only = np.asarray(text_rows, dtype=float)
    return text_only, np.hstack([text_only, np.asarray(structured_rows, dtype=float)])


def make_gbm() -> HistGradientBoostingClassifier:
    return HistGradientBoostingClassifier(
        max_iter=300,
        learning_rate=0.06,
        max_leaf_nodes=31,
        l2_regularization=1.0,
        class_weight="balanced",
        random_state=D.SEED,
    )


@dataclass
class Candidate:
    name: str
    servable: bool
    val_scores: np.ndarray
    test_fn: Callable[[], np.ndarray]


def tune_lr(x_train, y_train, x_val, y_val) -> tuple[float, dict[str, float]]:
    """Pick C by validation PR-AUC on an uncalibrated LR (calibration doesn't change ranking)."""
    results = {}
    for c in C_GRID:
        lr = LogisticRegression(C=c, class_weight="balanced", max_iter=3000, solver="liblinear")
        lr.fit(x_train, y_train)
        results[c] = score(y_val, lr.predict_proba(x_val)[:, 1]).pr_auc
        print(f"  LR C={c:<5} val PR-AUC={results[c]:.4f}")
    best = max(results, key=results.get)
    return best, {str(k): round(v, 4) for k, v in results.items()}


def main() -> None:
    path = D.find_dataset()
    raw = D.load_postings(path)
    df, dedupe_report = D.dedupe(raw)
    parts = D.split(df)
    y_train, y_val, y_test = (
        p["fraudulent"].to_numpy() for p in (parts.train, parts.val, parts.test)
    )
    print(
        f"rows {dedupe_report.rows_before} -> {dedupe_report.rows_after} after dedupe; "
        f"train {len(y_train)} val {len(y_val)} test {len(y_test)}"
    )

    synthetic = load_synthetic()
    overlap = set(parts.train["text"]) & {r["text"].lower() for r in synthetic}
    assert not overlap, "synthetic examples must never be in the training data"

    print("1) TF-IDF + logistic regression")
    vectorizer = make_vectorizer()
    xt_train = vectorizer.fit_transform(parts.train["text"])
    xt_val, xt_test = (
        vectorizer.transform(parts.val["text"]),
        vectorizer.transform(parts.test["text"]),
    )
    best_c, c_search = tune_lr(xt_train, y_train, xt_val, y_val)
    text_clf = calibrated(
        LogisticRegression(C=best_c, class_weight="balanced", max_iter=3000, solver="liblinear")
    ).fit(xt_train, y_train)

    print("2) gradient boosting on engineered features")
    (xf_train, xs_train), (xf_val, xs_val), (xf_test, xs_test) = (
        feature_matrices(p) for p in (parts.train, parts.val, parts.test)
    )
    gbm_text = calibrated(make_gbm()).fit(xf_train, y_train)
    gbm_full = calibrated(make_gbm()).fit(xs_train, y_train)

    lr_val = text_clf.predict_proba(xt_val)[:, 1]
    gt_val = gbm_text.predict_proba(xf_val)[:, 1]
    candidates = [
        Candidate("tfidf_logreg", True, lr_val, lambda: text_clf.predict_proba(xt_test)[:, 1]),
        Candidate("gbm_text_features", True, gt_val, lambda: gbm_text.predict_proba(xf_test)[:, 1]),
        Candidate(
            "gbm_text_plus_structured",
            False,
            gbm_full.predict_proba(xs_val)[:, 1],
            lambda: gbm_full.predict_proba(xs_test)[:, 1],
        ),
        Candidate(
            "blend_logreg_gbm_text",
            True,
            (lr_val + gt_val) / 2,
            lambda: (
                (text_clf.predict_proba(xt_test)[:, 1] + gbm_text.predict_proba(xf_test)[:, 1]) / 2
            ),
        ),
    ]
    val_table = {c.name: as_dict(score(y_val, c.val_scores)) for c in candidates}
    for name, s in val_table.items():
        print(f"  val {name:<26} PR-AUC={s['pr_auc']:.4f} R@P90={s['recall_at_90_precision']:.4f}")

    # Only text-computable models can be served on a pasted message.
    chosen = max((c for c in candidates if c.servable), key=lambda c: val_table[c.name]["pr_auc"])
    _, high = recall_at_precision(y_val, chosen.val_scores, TARGET_PRECISION)
    warn = min(threshold_for_recall(y_val, chosen.val_scores, TARGET_RECALL), high)
    print(f"chosen {chosen.name}: warn={warn:.4f} high={high:.4f}")

    # ---- the one and only look at the test set ----
    test_scores = {c.name: c.test_fn() for c in candidates}
    test_table = {name: as_dict(score(y_test, p)) for name, p in test_scores.items()}
    chosen_test = test_scores[chosen.name]

    model = LegitModel(
        vectorizer=vectorizer,
        text_clf=text_clf,
        gbm_text=gbm_text,
        mode="text" if chosen.name == "tfidf_logreg" else "blend",
        warn_threshold=warn,
        high_threshold=high,
        version=__version__,
        meta={"chosen": chosen.name, "lr_C": best_c},
    )
    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH, compress=3)

    synthetic_eval = evaluate_synthetic(model, synthetic)
    metrics = {
        "model_version": __version__,
        "dataset": {
            "file_sha256": D.file_sha256(path),
            "rows_raw": dedupe_report.rows_before,
            "rows_after_dedupe": dedupe_report.rows_after,
            "duplicate_groups_with_conflicting_labels": dedupe_report.conflicting_groups,
            "fake_rate": round(float(df["fraudulent"].mean()), 4),
            "split_sizes": {"train": len(y_train), "val": len(y_val), "test": len(y_test)},
            "split_positives": {
                "train": int(y_train.sum()),
                "val": int(y_val.sum()),
                "test": int(y_test.sum()),
            },
            "test_ids_fingerprint": D.ids_fingerprint(parts.test),
            "seed": D.SEED,
        },
        "lr_c_search_val_pr_auc": c_search,
        "validation": val_table,
        "chosen_model": chosen.name,
        "thresholds": {
            "warn": round(warn, 6),
            "high": round(high, 6),
            "rule": (
                f"high: precision>={TARGET_PRECISION} on val; warn: recall>={TARGET_RECALL} on val"
            ),
        },
        "test": test_table,
        "test_chosen_at_thresholds": {
            "warn": as_dict(at_threshold(y_test, chosen_test, warn)),
            "high": as_dict(at_threshold(y_test, chosen_test, high)),
        },
        "test_baselines": {
            "always_genuine_accuracy": round(float(1 - y_test.mean()), 4),
            "random_pr_auc": round(float(y_test.mean()), 4),
        },
        "synthetic_india": synthetic_eval,
        "environment": {"python": platform.python_version(), "sklearn": sklearn.__version__},
    }
    (MODELS_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    write_figures(
        y_val,
        {c.name: c.val_scores for c in candidates},
        y_test,
        test_scores,
        chosen.name,
        warn,
        high,
        gbm_full,
        xs_val,
    )
    print(
        json.dumps(
            {
                "test": test_table[chosen.name],
                "at_thresholds": metrics["test_chosen_at_thresholds"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
