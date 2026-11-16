"""Privacy-respecting usage counters: one row per (day, source, event), just a number."""

from __future__ import annotations

import logging
import os
from datetime import UTC, date, datetime
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

log = logging.getLogger("legitcheck.usage")
ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = ROOT / "migrations"
EVENTS = ("first_use", "check_consistent", "check_warning", "check_high_risk")


def database_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if url.startswith("postgres://"):  # Neon/Render style URLs
        url = "postgresql+psycopg://" + url.removeprefix("postgres://")
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url or f"sqlite:///{ROOT / 'legitcheck_usage.db'}"


def _statements(sql: str) -> list[str]:
    lines = [line for line in sql.splitlines() if not line.strip().startswith("--")]
    return [s.strip() for s in "\n".join(lines).split(";") if s.strip()]


class UsageStore:
    def __init__(self, url: str | None = None) -> None:
        self.engine: Engine = create_engine(url or database_url(), pool_pre_ping=True)

    def migrate(self) -> list[str]:
        """Apply migrations/*.sql in order, once each. Returns the names applied now."""
        applied_now = []
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    "CREATE TABLE IF NOT EXISTS schema_migrations "
                    "(name VARCHAR(128) PRIMARY KEY, applied_at TIMESTAMP NOT NULL)"
                )
            )
            done = {row[0] for row in conn.execute(text("SELECT name FROM schema_migrations"))}
            for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
                if path.name in done:
                    continue
                for statement in _statements(path.read_text(encoding="utf-8")):
                    conn.execute(text(statement))
                conn.execute(
                    text("INSERT INTO schema_migrations (name, applied_at) VALUES (:n, :t)"),
                    {"n": path.name, "t": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")},
                )
                applied_now.append(path.name)
        return applied_now

    def increment(self, source: str, event: str, day: date | None = None) -> None:
        if event not in EVENTS:
            raise ValueError(f"unknown event {event!r}")
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO usage_daily (day, source, event, count) "
                    "VALUES (:day, :source, :event, 1) "
                    "ON CONFLICT (day, source, event) DO UPDATE SET count = usage_daily.count + 1"
                ),
                # ISO strings: SQLite's date adapters are deprecated, Postgres casts them.
                {
                    "day": (day or datetime.now(UTC).date()).isoformat(),
                    "source": source,
                    "event": event,
                },
            )

    def safe_increment(self, source: str, event: str) -> None:
        """Counting must never break a check, so database errors are only logged."""
        try:
            self.increment(source, event)
        except Exception as exc:
            log.warning("usage count failed: %s", type(exc).__name__)

    def totals(self) -> dict[str, int]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                text("SELECT event, SUM(count) FROM usage_daily GROUP BY event")
            ).all()
        found = {event: int(total or 0) for event, total in rows}
        return {event: found.get(event, 0) for event in EVENTS}
