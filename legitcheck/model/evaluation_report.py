"""Render reports/evaluation.md from models/metrics.json, so no number is typed by hand.

Run: python -m legitcheck.model.evaluation_report
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METRICS = ROOT / "models" / "metrics.json"
OUT = ROOT / "reports" / "evaluation.md"
NAMES = {
    "tfidf_logreg": "TF-IDF + logistic regression (served)",
    "gbm_text_features": "Gradient boosting, text features",
    "gbm_text_plus_structured": "Gradient boosting, text + structured (not servable)",
    "blend_logreg_gbm_text": "Average of LR and text GBM",
}


def _table(results: dict[str, dict[str, float]]) -> list[str]:
    rows = [
        "| Model | PR-AUC | Recall @ 90% precision | ROC-AUC | Brier |",
        "|---|---|---|---|---|",
    ]
    for key, s in results.items():
        rows.append(
            f"| {NAMES[key]} | {s['pr_auc']:.3f} | {s['recall_at_90_precision']:.3f} | "
            f"{s['roc_auc']:.3f} | {s['brier']:.4f} |"
        )
    return rows


def _threshold_rows(at: dict[str, dict[str, float]]) -> list[str]:
    rows = [
        "| Threshold | Score cut-off | Precision | Recall | Caught | Missed | False alarms |",
        "|---|---|---|---|---|---|---|",
    ]
    for name in ("warn", "high"):
        a = at[name]
        rows.append(
            f"| {name} | {a['threshold']:.3f} | {a['precision']:.3f} | {a['recall']:.3f} | "
            f"{a['tp']} | {a['fn']} | {a['fp']} of {a['fp'] + a['tn']} genuine |"
        )
    return rows


def _synthetic_rows(section: dict) -> list[str]:
    rows = [
        "| Split | Messages | Model alone | Rules alone | Combined verdict |",
        "|---|---|---|---|---|",
    ]
    for split in ("dev", "holdout"):
        for label, wording in (("scam", "scams flagged"), ("genuine", "genuine flagged")):
            r = section[split][label]
            cells = [
                f"{r[k]['flagged']}/{r[k]['total']}"
                for k in ("model_only", "rules_only", "combined")
            ]
            rows.append(f"| {split} | {wording} | " + " | ".join(cells) + " |")
    return rows


def render(m: dict) -> str:
    d = m["dataset"]
    lines = [
        "# Evaluation",
        "",
        "Generated from `models/metrics.json` by `python -m legitcheck.model.evaluation_report`.",
        "",
        "## Data and split",
        "",
        f"- {d['rows_raw']:,} postings; {d['rows_raw'] - d['rows_after_dedupe']:,} exact "
        f"duplicates removed before splitting, leaving {d['rows_after_dedupe']:,} "
        f"({d['fake_rate']:.1%} fake). {d['duplicate_groups_with_conflicting_labels']} duplicate "
        "groups had conflicting labels and were marked fake.",
        f"- Stratified split (seed {d['seed']}): train {d['split_sizes']['train']:,} / "
        f"validation {d['split_sizes']['val']:,} / test {d['split_sizes']['test']:,}; "
        f"fake postings {d['split_positives']['train']} / {d['split_positives']['val']} / "
        f"{d['split_positives']['test']}.",
        f"- Dataset SHA-256 `{d['file_sha256'][:16]}...`, test-id fingerprint "
        f"`{d['test_ids_fingerprint']}`.",
        "",
        "## Validation (used to choose the model and the thresholds)",
        "",
        *_table(m["validation"]),
        "",
        f"Chosen for serving: **{NAMES[m['chosen_model']]}**, the best validation PR-AUC among "
        "models that can run on pasted text. Thresholds: " + m["thresholds"]["rule"] + ".",
        "",
        "## Test (evaluated once)",
        "",
        *_table(m["test"]),
        "",
        f"Baselines: predicting 'genuine' for everything is "
        f"{m['test_baselines']['always_genuine_accuracy']:.1%} accurate and useless; a random "
        f"score has PR-AUC {m['test_baselines']['random_pr_auc']:.3f}.",
        "",
        "### Served model at the validation thresholds",
        "",
        *_threshold_rows(m["test_chosen_at_thresholds"]),
        "",
        "![PR curve](figures/pr_test.png) ![Calibration](figures/calibration_test.png)",
        "",
        "![Confusion matrices](figures/confusion_test.png)",
        "",
        "## SYNTHETIC India set (separate, never trained on)",
        "",
        "Written for this project with fictional companies. *dev* examples were used while "
        "writing the rules; *holdout* examples were written afterwards and only scored. "
        "'Model alone' uses the warning threshold at every length.",
        "",
        "Current verdict logic:",
        "",
        *_synthetic_rows(m["synthetic_india"]),
        "",
        "First version, before the short-message rule:",
        "",
        *_synthetic_rows(m["synthetic_india_before_short_text_rule"]),
        "",
        "## Gradient boosting: which engineered features matter",
        "",
        "![Permutation importance](figures/gbm_importance_val.png)",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    OUT.write_text(render(json.loads(METRICS.read_text(encoding="utf-8"))), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
