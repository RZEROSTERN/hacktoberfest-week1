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

## 2026-10-04: Model spike results (`gemma4:e4b`, prompt `analyze_v1`)

Script: `api/scripts/spike_samples.py`. Request: Ollama `/api/chat` with the image as base64
in `images`, the Pydantic JSON schema in `format` and in the prompt, `temperature: 0`.

| Sample | Expected | Thinking on (default) | Thinking off, original prompt | Thinking off, final prompt |
|---|---|---|---|---|
| SAT Constancia de Situación Fiscal | no deadline, no amount | correct, ~74 s | **wrong: issue date 2026-08-20 reported as deadline**, ~48 s | correct, 22–26 s |
| Telmex bill, $2,798.00, "pagar antes de: INMEDIATO" | no date, $2,798.00 | correct, 55–59 s | correct, ~18 s | correct, 10–25 s |

Decisions:
- **Spanish reading quality is good enough to continue**: document type, issuer and amount
  were right in every run, and the explanations are plain Mexican Spanish ("usted").
- **Disable thinking (`think: false`)**: Gemma 4 thinks by default in Ollama, spending about
  1,100 hidden tokens per photo and roughly doubling latency. With thinking off, output is
  about 180 tokens.
- **Spell out what a deadline is in the prompt**: turning thinking off made the model confuse
  the SAT issue date with a deadline. The prompt now lists what counts as a deadline
  ("fecha límite", "pagar antes de", "vence") and what doesn't (issue, emission, billing
  dates; "inmediato"). That fixed it in two consecutive runs.
- Caveat: only two samples, and neither has a printed due date, so positive deadline
  extraction is only covered by a text-only check ("Fecha límite de pago: 18 OCT 2026"
  → `2026-10-18`). The web loading state must be designed for waits of up to ~30 s.

## 2026-10-04: `/documents/analyze` design

- **Access control**: every `/documents` route requires an `X-Access-Code` header matching
  `ACCESS_CODE` (constant-time comparison). An empty `ACCESS_CODE` rejects everything, so a
  misconfigured deploy fails closed. The web app's server adds the header; the browser never
  sees the code.
- **Upload validation before the model**: content type must be JPEG, PNG or WEBP, the size
  is checked against `MAX_IMAGE_BYTES` (10 MB) both from the declared size and while reading,
  and the first bytes must match the format's signature. Rejections return 401/413/415
  without calling the model.
- **In-memory only**: the upload is read into a `bytes` object, base64-encoded for Ollama and
  dropped; nothing touches disk. Logs record only failure types (e.g. `ReadTimeout`), never
  prompts, images or model output.
- **Retry policy**: invalid model output (fails Pydantic validation) is retried once. A
  second invalid output, a timeout or a connection error returns a fixed low-confidence
  "No se pudo leer" result that asks for another photo; a model failure never becomes a 500.
- **What gets saved**: only results with `high`/`medium` confidence are stored in SQLite
  (structured fields only). Low-confidence results are returned with `id: null` and not saved,
  so the history never shows unreadable documents.
- Async tests use `pytest-asyncio` in auto mode; the Ollama client accepts an injectable
  `httpx` transport so tests mock the model with `httpx.MockTransport`.

## 2026-10-04: History and calendar reminder

- `GET /documents` returns the whole history newest first. No pagination: one user and a few
  documents a month. "Upcoming deadlines" are derived on the web side from the same list.
- `GET /documents/{id}` backs the result and history detail screens.
- `GET /documents/{id}/reminder.ics` is hand-written RFC 5545 (escaping and 75-octet line
  folding included) instead of adding an `icalendar` dependency: one all-day event on the due
  date with two display alarms, 3 days and 1 day before. It returns 404 when the document has
  no deadline, so the web app only shows "Agregar a mi calendario" when there is one.
