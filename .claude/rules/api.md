---
paths:
  - "api/**"
---

# API rules

- Config only via pydantic-settings (`app/config.py`) and `.env`; no `os.environ` reads.
- Validate every model output with Pydantic. On invalid output retry once, then return a
  low-confidence result; never guess fields.
- Ollama calls are async (httpx) with explicit timeouts. A model failure or timeout must
  never crash a request: return a low-confidence result or a clean HTTP error.
- Prompts live in `api/prompts/` as versioned files (e.g. `analyze_v1.md`), never inline.
- Unit tests mock the model. One `@pytest.mark.integration` test hits the real model using
  `/samples`.
- Validate upload content type and size before reading the body into the model.
- Read uploads into memory only; never save them, never log their bytes or the extracted text.
