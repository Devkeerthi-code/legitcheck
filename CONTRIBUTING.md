# Contributing

Thanks for helping make offer scams easier to spot.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cd web && npm ci
```

## Checks before a PR

```bash
ruff check . && ruff format --check .
pytest
cd web && npm run lint && npm test && npm run build
```

## Adding a rule

Rules live in `legitcheck/rules/`. Each rule returns the exact phrase it matched, so the UI
can highlight it. Add positive and negative test cases to `tests/test_rules.py`.
