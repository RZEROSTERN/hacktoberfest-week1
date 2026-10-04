# API

FastAPI backend for Paperwork Translator, consumed by the frontend in `../web`.
Uses Gemma 4 through Ollama; no closed-model APIs at runtime.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and a running Ollama with the model pulled
(`ollama pull gemma4:e4b`). Copy `../.env.example` to `../.env` first.

```bash
uv sync
```

## Development Server

```bash
uv run fastapi dev app/main.py
```

Runs on `http://localhost:8000`; interactive docs at `/docs`.

## Checks

```bash
uv run ruff check . && uv run ruff format --check .   # lint
uv run mypy .                                         # typecheck
uv run pytest                                         # unit tests (model mocked)
uv run pytest -m integration                          # hits the real model with /samples
```

All checks except the integration tests also run in CI via `.github/workflows/api-tests.yml`.
