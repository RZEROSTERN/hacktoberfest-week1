---
paths:
  - "web/**"
---

# Web rules

- API base URL and access code only via `runtimeConfig` (server-only keys); no secrets in
  client code.
- Composables (`app/composables/`) make API calls; components stay presentational.
- All UI strings live in `i18n/locales/es.json` and `en.json` (same keys in both), never in
  components. Spanish is warm, simple Mexican ("usted"); English is warm and plain. Format
  money and dates through `useFormatters()`.
- Designed for an older, non-technical user: tap targets at least 56px, body text at least
  20px, WCAG AA contrast or better, one primary action per screen.
- Loading and error states are always visible and in plain language (both languages); never a
  silent failure.
