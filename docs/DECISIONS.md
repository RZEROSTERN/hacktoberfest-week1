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

## 2026-10-04: Web photo flow

- **Nuxt server as a thin proxy (BFF)**: the browser only talks to `/api/*` on the Nuxt
  server. `server/api/documents/**` forwards to FastAPI with `proxyRequest` and adds the
  `X-Access-Code` header from server-only `runtimeConfig`, so the API URL and code never
  reach the browser and there is no CORS to configure.
- **Family access code**: `/acceso` posts the code to `/api/login`, which sets an `httpOnly`,
  `SameSite=Lax`, 1-year cookie (`Secure` outside dev). A Nitro server middleware redirects
  pages to `/acceso` and returns 401 for `/api/*` without a valid cookie (constant-time
  comparison; an empty configured code rejects everyone). The submit button stays disabled
  until hydration so an early tap can't fall back to a native form submit.
- **Camera capture**: a hidden `<input type="file" accept="image/*" capture="environment">`
  opened by the big "Tomar foto" button. No `getUserMedia` viewfinder: the native camera UI
  is familiar, works on iOS and Android, and needs no permission prompt.
- **Resize in the browser**: photos are downscaled to at most 1600 px and re-encoded as JPEG
  (quality 0.85) with `createImageBitmap` + canvas before upload. Phone photos are 3–8 MB;
  this makes upload and inference faster and normalizes HEIC/orientation. If resizing
  fails, the original file is sent and the API validates it.
- **Navigation**: saved results go to `/documentos/{id}` (shareable, reload-safe, SSR with
  the cookie forwarded by `useRequestFetch`); unsaved low-confidence results go to
  `/resultado` from in-memory state.
- **Accessibility baseline**: 20 px root font, 72 px buttons, AA+ contrast, `role="status"`
  loading and `role="alert"` errors, fraud warning first and in red, no-advice disclaimer on
  every result.
- Verified end to end with headless Chrome at 390×844: access gate, wrong/right code,
  "Tomar foto" → Telmex sample → result in 26.8 s with the correct amount and no invented
  deadline, reload works, no page errors.

## 2026-10-04: History screen and PWA

- **History** (`/documentos`): "Próximas fechas" (deadlines today or later, soonest first,
  with "Hoy / Mañana / En N días") above "Todos mis papeles" (newest first). Suspicious
  documents get a red border and a "Posible fraude" badge. The split is a pure function
  (`splitHistory`) so it is unit-tested without the API.
- **PWA via `@vite-pwa/nuxt` 1.1.1** with `registerType: 'autoUpdate'`, a Spanish manifest
  (`standalone`, portrait, theme `#0b4f9c`) and 192/512/maskable icons.
- **Service worker caches static assets only** (`js, css, png, svg, ico`) and sets
  `navigateFallback: null`: pages are server-rendered behind the access cookie, and
  documents or API responses must never sit in a cache on the phone. The app needs a
  connection anyway because the model runs on the server.
- **Icons**: a hand-written SVG (document + check mark) rendered to PNG with headless Chrome;
  no emoji artwork (licensing) and no image-processing dependency.
- Verified on the production build: manifest linked, service worker active, history split
  correct, and the calendar button downloads an `.ics` with alarms 3 days and 1 day before.

## 2026-10-04: Voice questions

- **No native Gemma 4 audio through Ollama**: `ollama show gemma4:e4b` lists an `audio`
  capability, but the `/api/chat` docs only document `images` for multimodal input and never
  mention audio. Per the "don't rely on undocumented APIs" rule, voice uses the planned
  fallback: speech-to-text with **faster-whisper** (MIT), then the text goes to Gemma 4.
  Worth revisiting once Ollama documents audio input.
- **Whisper `small`, CPU, int8**, Spanish forced (`language="es"`), VAD filter on. Transcribes
  a short question in ~1–2 s on an M2 Pro. Weights (~460 MB) download on first use into
  `api/.models/` (gitignored), not `~/.cache`.
- **In memory only**: `transcribe()` accepts a `BinaryIO`, so the upload goes through
  `io.BytesIO` and PyAV decodes it without touching disk. Transcripts are not logged or saved.
- **PyAV pinned `<17`**: faster-whisper 1.2.1 calls `av.open(..., metadata_errors=...)`, which
  newer PyAV (19.x) removed (`TypeError`). 16.1 works.
- **Accepted formats**: whatever `MediaRecorder` produces: `audio/webm` and `audio/ogg`
  (Chrome/Android) and `audio/mp4` (Safari/iOS), plus mpeg/wav. Codec parameters are
  stripped before the check. Decoding failures return 422 with a friendly message; empty
  transcripts return "No le escuché bien…" without calling the model.
- **Context for questions about a document**: only the stored structured fields (type,
  issuer, deadline, amount, actions, fraud flag/reason, explanation) go into the prompt.
  The prompt is fully rendered before user text is inserted, so a transcript containing
  `{schema}` can't alter it (a unit test caught the original re-templating bug).
- **Recording UX**: one "Empezar a hablar" button, a pulsing red dot with a seconds counter,
  one big "Ya terminé" button, auto-stop at 60 s. Each document page has "Preguntar sobre
  este papel".
- Test sample: `samples/question_telmex.m4a`, generated with macOS `say` and the natural
  es-MX "Paulina" voice. Novelty voices ("Grandma", "Eddy", "Flo") transcribed badly, but
  they're synthetic effects, not representative of real speech.
- Verified end to end: Chrome MediaRecorder (webm/opus) → Nuxt proxy → Whisper → Gemma 4,
  answered from the Telmex data in 8.9 s with the right amount and no invented date. The
  headless browser's microphone was replaced with a Web Audio stream playing the sample,
  because `getUserMedia` hangs for automated Chrome on macOS. Not yet tested on a real
  phone (especially iOS Safari's `audio/mp4`).

## 2026-10-04: Production deployment

- **Render has no GPUs**: its docs never mention them and the biggest instances are CPU-only
  (up to 12 CPU). Options considered: a smaller Gemma 4 on Render CPU, a DigitalOcean GPU
  Droplet, or the developer's Mac behind a tunnel.
- **Spike for the CPU option** (`gemma4:e2b`, Ollama forced to CPU with `num_gpu: 0` on a
  12-core M2 Pro): reading quality was acceptable (right amount, no invented dates, no false
  fraud flags), but processing one new photo took 379 s at full size, 127 s at 1024 px and
  67 s at 768 px. Render's shared vCPUs would likely be slower, so 2–5 minutes per photo.
  Rejected for UX.
- **Chosen: DigitalOcean GPU Droplet** (NVIDIA RTX 4000 Ada, 20 GB VRAM, $0.76/h, billed per
  second) running the already-validated `gemma4:e4b`. Render still hosts web + API from
  `master` as planned.
- **Demo window: 3 days** (Sun Oct 4 – Wed Oct 7, 2026), then the droplet is destroyed. That
  bounds the cost (about $55) and is announced in the README.
- **Securing a public Ollama**: Ollama has no auth. On the droplet it binds to 127.0.0.1 only;
  Caddy terminates HTTPS (free hostname via sslip.io, Let's Encrypt certificate) and proxies
  only requests carrying `Authorization: Bearer <OLLAMA_API_KEY>`, sending
  `Host: localhost:11434` as the Ollama FAQ's proxy example does. The API sends the header
  when `OLLAMA_API_KEY` is set.
- **Render layout**: the API is a private service (`pserv`, `1c-2g` for Whisper) with a 2 GB
  disk for SQLite and Whisper weights; only the web service (`0.5c-512mb`) is public. The web
  service gets the API's private `host:port` via `fromService.property: hostport` (the proxy
  adds `http://`) and copies `ACCESS_CODE` with `fromService.envVarKey`, so the code is
  entered once. Region `virginia`, close to DigitalOcean's US-East GPU regions.
- Not verified before merging: `render.yaml` against a live Render account, and
  `setup.sh` on a real droplet (both need the owner's accounts).
