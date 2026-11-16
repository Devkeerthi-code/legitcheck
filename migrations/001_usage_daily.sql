-- Usage counts only. No submitted text, IPs or identifiers are ever stored.
-- Works on SQLite (local) and Postgres (production).
CREATE TABLE IF NOT EXISTS usage_daily (
    day     DATE        NOT NULL,
    source  VARCHAR(16) NOT NULL CHECK (source IN ('web', 'extension', 'api')),
    event   VARCHAR(32) NOT NULL CHECK (event IN (
                'first_use', 'check_consistent', 'check_warning', 'check_high_risk')),
    count   INTEGER     NOT NULL DEFAULT 0 CHECK (count >= 0),
    PRIMARY KEY (day, source, event)
);

-- /stats sums by event across all days.
CREATE INDEX IF NOT EXISTS ix_usage_daily_event_day ON usage_daily (event, day);
