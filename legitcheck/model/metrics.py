"""Metrics suited to a rare positive class, and threshold selection."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
)

TARGET_PRECISION = 0.90
TARGET_RECALL = 0.90


def recall_at_precision(y: np.ndarray, p: np.ndarray, min_precision: float) -> tuple[float, float]:
    """Best recall reachable with precision >= min_precision, and the threshold for it."""
    precision, recall, thresholds = precision_recall_curve(y, p)
    # precision/recall have one more entry than thresholds; drop the final (recall=0) point.
    ok = np.where(precision[:-1] >= min_precision)[0]
    if ok.size == 0:
        return 0.0, 1.0
    best = ok[np.argmax(recall[ok])]
    return float(recall[best]), float(thresholds[best])


def threshold_for_recall(y: np.ndarray, p: np.ndarray, min_recall: float) -> float:
    """Highest threshold that still catches at least `min_recall` of the positives."""
    _, recall, thresholds = precision_recall_curve(y, p)
    ok = np.where(recall[:-1] >= min_recall)[0]
    return float(thresholds[ok.max()]) if ok.size else float(thresholds.min())


@dataclass(frozen=True)
class Scores:
    pr_auc: float
    roc_auc: float
    brier: float
    recall_at_90_precision: float


def score(y: np.ndarray, p: np.ndarray) -> Scores:
    return Scores(
        pr_auc=float(average_precision_score(y, p)),
        roc_auc=float(roc_auc_score(y, p)),
        brier=float(brier_score_loss(y, p)),
        recall_at_90_precision=recall_at_precision(y, p, TARGET_PRECISION)[0],
    )


@dataclass(frozen=True)
class AtThreshold:
    threshold: float
    precision: float
    recall: float
    tn: int
    fp: int
    fn: int
    tp: int


def at_threshold(y: np.ndarray, p: np.ndarray, threshold: float) -> AtThreshold:
    pred = (p >= threshold).astype(int)
    tn, fp, fn, tp = (int(v) for v in confusion_matrix(y, pred, labels=[0, 1]).ravel())
    return AtThreshold(
        threshold=threshold,
        precision=tp / (tp + fp) if tp + fp else 0.0,
        recall=tp / (tp + fn) if tp + fn else 0.0,
        tn=tn,
        fp=fp,
        fn=fn,
        tp=tp,
    )


def as_dict(obj: Scores | AtThreshold) -> dict[str, float]:
    return {k: round(v, 6) if isinstance(v, float) else v for k, v in asdict(obj).items()}
