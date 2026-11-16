"""Load the Kaggle dataset, remove re-posted duplicates and make the fixed split."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from ..features import raw_posting_text
from ..text import combine_fields, dedupe_key

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
SEED = 42
VAL_SIZE = 0.15
TEST_SIZE = 0.15


def find_dataset(raw_dir: Path = RAW_DIR) -> Path:
    """Locate fake_job_postings.csv, also when Kaggle's zip extracted it into a folder."""
    matches = sorted(p for p in raw_dir.rglob("fake_job_postings.csv") if p.is_file())
    if not matches:
        raise FileNotFoundError(
            f"fake_job_postings.csv not found under {raw_dir}. "
            "See README > Data for download steps."
        )
    return matches[0]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_postings(path: Path | None = None) -> pd.DataFrame:
    """Read the CSV and add `text` (cleaned, for TF-IDF), `raw_text` and `key` columns."""
    df = pd.read_csv(path or find_dataset())
    records = df.to_dict(orient="records")
    df["text"] = [combine_fields(r) for r in records]
    df["raw_text"] = [raw_posting_text(r) for r in records]
    df["key"] = df["text"].map(dedupe_key)
    return df


@dataclass(frozen=True)
class DedupeReport:
    rows_before: int
    rows_after: int
    conflicting_groups: int


def dedupe(df: pd.DataFrame) -> tuple[pd.DataFrame, DedupeReport]:
    """Keep one row per identical posting text.

    Without this, copies of the same ad land in train and test and inflate the scores.
    If copies disagree on the label, the group is marked fake (the conservative choice).
    """
    labels = df.groupby("key")["fraudulent"].agg(["max", "min"])
    conflicting = int((labels["max"] != labels["min"]).sum())
    out = df.drop_duplicates("key", keep="first").copy()
    out["fraudulent"] = out["key"].map(labels["max"]).astype(int)
    return out.reset_index(drop=True), DedupeReport(len(df), len(out), conflicting)


@dataclass(frozen=True)
class Split:
    train: pd.DataFrame
    val: pd.DataFrame
    test: pd.DataFrame


def split(df: pd.DataFrame, seed: int = SEED) -> Split:
    """Stratified 70/15/15 split so each part keeps the ~5% fake rate."""
    train_val, test = train_test_split(
        df, test_size=TEST_SIZE, stratify=df["fraudulent"], random_state=seed
    )
    val_fraction = VAL_SIZE / (1 - TEST_SIZE)
    train, val = train_test_split(
        train_val, test_size=val_fraction, stratify=train_val["fraudulent"], random_state=seed
    )
    return Split(
        train.reset_index(drop=True), val.reset_index(drop=True), test.reset_index(drop=True)
    )


def ids_fingerprint(frame: pd.DataFrame) -> str:
    """Short hash of the job ids in a split, to prove the same split is reused."""
    joined = ",".join(map(str, sorted(frame["job_id"].tolist())))
    return hashlib.sha256(joined.encode()).hexdigest()[:16]
