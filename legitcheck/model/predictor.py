"""The served model: calibrated scores plus word-level explanations."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer

from ..features import TEXT_FEATURES, text_features
from ..text import clean_text

MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "legitcheck.joblib"


@dataclass(frozen=True)
class Contribution:
    term: str
    weight: float  # positive pushes towards "fake", negative towards "genuine"


@dataclass
class LegitModel:
    """Bundle saved by training. `mode` is "text" (LR only) or "blend" (LR + text-GBM mean)."""

    vectorizer: TfidfVectorizer
    text_clf: CalibratedClassifierCV
    gbm_text: CalibratedClassifierCV
    mode: str
    warn_threshold: float
    high_threshold: float
    version: str
    meta: dict[str, object] = field(default_factory=dict)

    @cached_property
    def _term_names(self) -> np.ndarray:
        # get_feature_names_out() rebuilds a 60k-entry array on every call; build it once.
        return self.vectorizer.get_feature_names_out()

    @cached_property
    def _coef(self) -> np.ndarray:
        return self.text_clf.calibrated_classifiers_[0].estimator.coef_[0]

    def text_scores(self, cleaned: Sequence[str]) -> np.ndarray:
        return self.text_clf.predict_proba(self.vectorizer.transform(cleaned))[:, 1]

    def gbm_scores(self, raw: Sequence[str]) -> np.ndarray:
        rows = [[text_features(t)[name] for name in TEXT_FEATURES] for t in raw]
        return self.gbm_text.predict_proba(np.asarray(rows, dtype=float))[:, 1]

    def score_texts(self, raw: Sequence[str], cleaned: Sequence[str] | None = None) -> np.ndarray:
        cleaned = cleaned if cleaned is not None else [clean_text(t) for t in raw]
        lr = self.text_scores(cleaned)
        if self.mode == "text":
            return lr
        return (lr + self.gbm_scores(raw)) / 2

    def score(self, text: str) -> float:
        return float(self.score_texts([text])[0])

    def contributions(self, text: str, k: int = 8) -> list[Contribution]:
        """Exact per-term contributions to the logistic-regression logit (coef * tf-idf).

        Calibration is a monotonic sigmoid on top, so the ranking of terms is unchanged.
        """
        x = self.vectorizer.transform([clean_text(text)])
        names, idx = self._term_names, x.indices
        weights = x.data * self._coef[idx]
        order = np.argsort(-np.abs(weights))[:k]
        return [Contribution(str(names[idx[i]]), round(float(weights[i]), 4)) for i in order]


def load_model(path: Path = MODEL_PATH) -> LegitModel:
    model = joblib.load(path)
    if not isinstance(model, LegitModel):
        raise TypeError(f"{path} does not contain a LegitModel")
    return model
