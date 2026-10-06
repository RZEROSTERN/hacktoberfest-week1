# Paperwork Translator

Mobile-first PWA for an older, non-technical user: she photographs a document (CFE bill,
bank letter, SAT notice, summons) or asks by voice, and gets a plain explanation in Mexican
Spanish (default) or English, her choice: what it is, deadline/amount, steps to take, and a
fraud warning. Runtime AI is Gemma 4 via Ollama only. Built for the DEV Hacktoberfest Weekend
Challenge 2026.

- `api/` FastAPI, Python 3.12, uv, SQLModel/SQLite. Prompts in `api/prompts/`.
- `web/` Nuxt 4, TypeScript strict, PWA, UI strings in `web/i18n/locales/{es,en}.json`.
- `samples/` anonymized test documents (the only documents allowed in tests and demos).
- `docs/DECISIONS.md` technical decision log.

## Commands

- Install: `cd api && uv sync` · `cd web && npm install`
- Ollama: `brew services start ollama` · `ollama pull gemma4:e4b`
- Run api: `cd api && uv run fastapi dev app/main.py` (port 8000)
- Run web: `cd web && npm run dev` (port 3000)
- Test: `cd api && uv run pytest` (`-m integration` hits the real model) · `cd web && npm test`
- Lint: `cd api && uv run ruff check . && uv run ruff format --check .` · `cd web && npm run lint`
- Typecheck: `cd api && uv run mypy .` · `cd web && npm run typecheck`
- Full stack: `docker compose up` (copy `.env.example` to `.env` first)

## Git: GitFlow, no stacked PRs

- `master` is production (there is no `main`). `develop` is integration.
- Never commit to `master` or `develop` directly.
- `feature/<name>` from the latest `develop` → one PR with `--base develop`.
- `release/<x.y.z>` from `develop` → PR into `master`, tag, merge `master` back into `develop`.
  `hotfix/<name>` from `master` → PR into `master`, merge back into `develop`.
- Never branch from another feature branch; never target any other base.
- Merge with a merge commit and delete the branch: `gh pr merge --merge --delete-branch`.
- PR body: what changed, why, how it was tested, whether DECISIONS.md was updated.

## Workflow

- Before each commit, run lint + typecheck + tests for the part you touched.
- Conventional Commits for commits and PR titles.
- Update `docs/DECISIONS.md` whenever a technical decision is made or changed.
- Check official docs instead of guessing Ollama, Nuxt or Render APIs and flags; say so
  when something isn't documented.
- Commits after Mon 2026-10-05 00:59 (Mexico City) must be listed in the README.

## Non-negotiables

- No closed-model APIs at runtime (no Claude, OpenAI, Gemini).
- Images and audio are processed in memory only: never written to disk or logs.
- Never log document contents or personal data. Secrets only in `.env`.
- All user-facing text exists in Spanish (the default: Mexican, warm, simple, "usted") and
  English (warm, plain); every key in both files. Everything else (code, logs, docs) in English.
- The AI explains only: no legal/financial advice, never invents amounts or dates, never
  asks for passwords, PINs, card or ID numbers.

## Gotchas

- `npm ci` fails on Linux with a macOS-generated lockfile (missing `@emnapi/*`); CI and the
  web Dockerfile use `npm install`.
- Docker on macOS can't use the GPU: run Ollama natively on Macs.
- Gemma 4 thinks by default in Ollama: send `"think": false` (2x faster) and keep the
  explicit deadline rules in the prompt, or it mistakes issue dates for deadlines.
- PyAV is pinned `<17`: faster-whisper 1.2.1 breaks on newer PyAV (`metadata_errors`).
- `@nuxtjs/i18n` doesn't set `<html lang>` (`app.vue` does) and loads the other language from
  `/_i18n/…`, which must stay in the access middleware's public paths. happy-dom reports
  `en-US`, so `test/setup.ts` pins Spanish before each test.
- Automated Chrome on macOS hangs on `getUserMedia`; e2e tests stub the mic with Web Audio.
