# Technical decisions

A running log of technical decisions and why they were made. Newest last.

## 2026-10-04: Branching model

- GitFlow with non-stacked PRs. `master` is the production branch (there is no `main`);
  `develop` is the integration branch. Every feature branch starts from the latest `develop`
  and merges back through its own PR; release and hotfix PRs target `master`.
- Why: one reviewable PR per build step, and `master` always matches what is deployed.

## 2026-10-04: Model and runtime

- Model: `gemma4:e4b` via Ollama (Apache 2.0). About 6.6 GB on disk, fits a 16 GB
  M2 Pro alongside the API and web dev servers.
- Why e4b over 12b: Gemma's model card lists audio input for the E2B/E4B variants, which may
  let voice questions skip a separate speech-to-text model. 12b may read documents better
  and is the fallback if the spike shows poor extraction quality.
- Ollama runs natively on macOS (Homebrew service), not in Docker, because Docker on macOS
  cannot use the Apple GPU (Metal). `docker-compose.yml` still ships an Ollama service for
  Linux/GPU machines.

## 2026-10-04: API stack

- FastAPI + Python 3.12, managed with uv (`uv.lock` committed, `package = false` since this
  is an app, not a library).
- SQLModel on SQLite: a single family user and a handful of documents do not need a server
  database.
- Config only through pydantic-settings, read from environment variables or `.env`.
- Quality gates: ruff (lint + format), mypy in strict mode, pytest. Tests marked
  `integration` hit the real model and are deselected by default.

## 2026-10-04: Web stack

- Nuxt 4 (TypeScript strict), official `@nuxt/eslint` module for linting, `nuxt typecheck`
  (vue-tsc) for typechecking, Vitest + `@nuxt/test-utils` for unit tests.
- The API base URL and access code live in server-only `runtimeConfig`, so neither is shipped
  to the browser.

## 2026-10-04: Local dev and CI

- `docker-compose.yml` runs Ollama + API + web; the `.env` file is optional so
  `docker compose config` works on a fresh clone.
- GitHub Actions run lint, typecheck and unit tests per folder, only when that folder changes,
  on pushes to `master`/`develop` and on PRs. uv is installed with the pinned
  `astral-sh/setup-uv` action from the uv docs.

## 2026-10-04: `npm install` instead of `npm ci` on Linux

- A `package-lock.json` generated on macOS omits some platform-specific optional packages
  (`@emnapi/*` WASM fallbacks), so `npm ci` on Linux fails with "Missing ... from lock file"
  even after regenerating the lockfile. CI and the web Dockerfile use
  `npm install --no-audit --no-fund`, which still honors the lockfile's pinned versions.
