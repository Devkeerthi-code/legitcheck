"""Plots for the evaluation report (PR curves, calibration, confusion matrix, importances)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.inspection import permutation_importance  # noqa: E402
from sklearn.metrics import precision_recall_curve  # noqa: E402

from ..features import STRUCTURED_FEATURES, TEXT_FEATURES  # noqa: E402

FIG_DIR = Path(__file__).resolve().parents[2] / "reports" / "figures"
INK, ACCENT, MUTED = "#0E2A22", "#1F4BD8", "#8A9C95"
PALETTE = [ACCENT, "#17603F", "#8A4B00", "#B42318"]


def _style(ax: plt.Axes, title: str) -> None:
    ax.set_title(title, loc="left", fontsize=11, color=INK)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.25)


def _pr_plot(y: np.ndarray, scores: dict[str, np.ndarray], title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for color, (name, p) in zip(PALETTE, scores.items(), strict=False):
        precision, recall, _ = precision_recall_curve(y, p)
        ax.plot(recall, precision, label=name, color=color, lw=1.6)
    ax.axhline(y.mean(), color=MUTED, ls="--", lw=1, label=f"random ({y.mean():.3f})")
    ax.set_xlabel("Recall (share of fake postings caught)")
    ax.set_ylabel("Precision (share of flags that are fake)")
    ax.legend(fontsize=8, frameon=False)
    _style(ax, title)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _calibration_plot(y: np.ndarray, p: np.ndarray, name: str, path: Path) -> None:
    """Uniform bins, with the posting count per bin, since most scores sit near zero."""
    edges = np.linspace(0, 1, 11)
    bins = np.clip(np.digitize(p, edges) - 1, 0, 9)
    fig, ax = plt.subplots(figsize=(5.2, 4.5))
    ax.plot([0, 1], [0, 1], color=MUTED, ls="--", lw=1, label="perfect")
    xs, ys = [], []
    for b in range(10):
        mask = bins == b
        if mask.sum() == 0:
            continue
        xs.append(p[mask].mean())
        ys.append(y[mask].mean())
        ax.annotate(
            f"n={mask.sum()}",
            (xs[-1], ys[-1]),
            textcoords="offset points",
            xytext=(4, -10),
            fontsize=7,
            color=MUTED,
        )
    ax.plot(xs, ys, marker="o", color=ACCENT, lw=1.6, label=name)
    ax.set_xlabel("Predicted probability")
    ax.set_ylabel("Observed fake rate")
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    _style(ax, "Calibration on test (10 equal-width bins)")
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _confusion_plot(y: np.ndarray, p: np.ndarray, thresholds: dict[str, float], path: Path) -> None:
    fig, axes = plt.subplots(1, len(thresholds), figsize=(8, 3.6))
    for ax, (label, t) in zip(axes, thresholds.items(), strict=True):
        pred = p >= t
        cm = np.array(
            [
                [np.sum(~pred & (y == 0)), np.sum(pred & (y == 0))],
                [np.sum(~pred & (y == 1)), np.sum(pred & (y == 1))],
            ]
        )
        ax.imshow(cm, cmap="Greens")
        for (i, j), v in np.ndenumerate(cm):
            ax.text(j, i, str(v), ha="center", va="center", color=INK, fontsize=12)
        ax.set_xticks([0, 1], ["flagged: no", "flagged: yes"])
        ax.set_yticks([0, 1], ["genuine", "fake"])
        ax.set_title(f"{label} threshold ({t:.2f})", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _importance_plot(model: object, x: np.ndarray, y: np.ndarray, path: Path) -> None:
    names = list(TEXT_FEATURES) + list(STRUCTURED_FEATURES)
    result = permutation_importance(
        model, x, y, scoring="average_precision", n_repeats=5, random_state=42, n_jobs=1
    )
    order = np.argsort(result.importances_mean)[-15:]
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.barh([names[i] for i in order], result.importances_mean[order], color=ACCENT)
    ax.set_xlabel("Drop in validation PR-AUC when shuffled")
    _style(ax, "GBM (text + structured): permutation importance")
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def write_figures(
    y_val, val_scores, y_test, test_scores, chosen, warn, high, gbm_full, xs_val
) -> None:
    """Save all evaluation plots. `gbm_full` and `xs_val` feed the importance plot."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    _pr_plot(y_val, val_scores, "Precision-recall on validation", FIG_DIR / "pr_validation.png")
    _pr_plot(y_test, test_scores, "Precision-recall on test", FIG_DIR / "pr_test.png")
    _calibration_plot(y_test, test_scores[chosen], chosen, FIG_DIR / "calibration_test.png")
    _confusion_plot(
        y_test, test_scores[chosen], {"warn": warn, "high": high}, FIG_DIR / "confusion_test.png"
    )
    _importance_plot(gbm_full, xs_val, y_val, FIG_DIR / "gbm_importance_val.png")
