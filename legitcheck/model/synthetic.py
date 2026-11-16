"""Separate evaluation on the SYNTHETIC India set (never used for training)."""

from __future__ import annotations

import json
from pathlib import Path

from ..rules import Severity, run_rules
from ..verdict import Verdict, decide, model_is_reliable
from .predictor import LegitModel

SYNTHETIC_PATH = Path(__file__).resolve().parents[2] / "data" / "synthetic" / "india_offers.jsonl"


def load_synthetic(path: Path = SYNTHETIC_PATH) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        records = [json.loads(line) for line in handle if line.strip()]
    assert all(r["synthetic"] is True for r in records), "every record must be marked synthetic"
    return records


def _rate(flags: list[bool]) -> dict[str, float]:
    return {
        "flagged": sum(flags),
        "total": len(flags),
        "rate": round(sum(flags) / len(flags), 4) if flags else 0.0,
    }


def evaluate_synthetic(model: LegitModel, records: list[dict]) -> dict[str, object]:
    """How often each layer flags scams (want high) and genuine messages (want low)."""
    scores = model.score_texts([r["text"] for r in records])
    out: dict[str, object] = {"note": "SYNTHETIC examples written for this project, not real data."}
    for split in ("dev", "holdout"):
        rows = [(r, float(s)) for r, s in zip(records, scores, strict=True) if r["split"] == split]
        table: dict[str, dict[str, dict[str, float]]] = {}
        for label in ("scam", "genuine"):
            subset = [(r, s) for r, s in rows if r["label"] == label]
            model_flags, rule_flags, combined_flags = [], [], []
            for r, s in subset:
                hits = run_rules(r["text"], r["url"], r["email"])
                model_flags.append(s >= model.warn_threshold)
                rule_flags.append(any(h.severity in (Severity.HIGH, Severity.MEDIUM) for h in hits))
                decision = decide(
                    s,
                    hits,
                    model.warn_threshold,
                    model.high_threshold,
                    model_is_reliable(r["text"]),
                )
                combined_flags.append(decision.verdict != Verdict.CONSISTENT)
            table[label] = {
                "model_only": _rate(model_flags),
                "rules_only": _rate(rule_flags),
                "combined": _rate(combined_flags),
            }
        out[split] = table
    out["model_scores"] = {
        r["id"]: round(float(s), 6) for r, s in zip(records, scores, strict=True)
    }
    return out


def main() -> None:
    """Re-score only the synthetic set and update metrics.json (the test set is not touched)."""
    from .predictor import MODEL_PATH, load_model

    metrics_path = MODEL_PATH.parent / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics["synthetic_india"] = evaluate_synthetic(load_model(), load_synthetic())
    payload = json.dumps(metrics, indent=2, ensure_ascii=False) + "\n"
    metrics_path.write_text(payload, encoding="utf-8")
    summary = {k: v for k, v in metrics["synthetic_india"].items() if k != "model_scores"}
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
