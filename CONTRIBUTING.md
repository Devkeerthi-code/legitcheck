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
