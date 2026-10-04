"""Async client for Gemma 4 via Ollama. Never logs prompts, images or model output."""

import base64
import json
import logging
from functools import lru_cache
from pathlib import Path

import httpx
from pydantic import ValidationError

from app.config import Settings, get_settings
from app.schemas import DocumentAnalysis

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
ANALYZE_PROMPT = "analyze_v1.md"
MAX_ATTEMPTS = 2  # first try + one retry


@lru_cache
def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def unreadable_result() -> DocumentAnalysis:
    """Returned instead of guessing when the model fails or gives invalid output."""
    return DocumentAnalysis(
        document_type="No se pudo leer",
        issuer=None,
        deadline=None,
        amount_due=None,
        required_actions=["Tome otra foto con buena luz, con la hoja completa y sin moverse."],
        is_suspicious=False,
        fraud_reason=None,
        confidence="low",
        explanation=(
            "No pude leer bien este papel. ¿Me ayuda tomando otra foto? "
            "Ponga la hoja sobre una mesa, con buena luz y que se vea completa."
        ),
    )


class OllamaClient:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self._settings = settings
        self._transport = transport

    async def _chat(self, payload: dict[str, object]) -> str:
        async with httpx.AsyncClient(
            base_url=self._settings.ollama_base_url,
            timeout=self._settings.ollama_timeout_seconds,
            transport=self._transport,
        ) as client:
            response = await client.post("/api/chat", json=payload)
            response.raise_for_status()
            content: str = response.json()["message"]["content"]
            return content

    async def analyze_document(self, image: bytes) -> DocumentAnalysis:
        schema = DocumentAnalysis.model_json_schema()
        prompt = load_prompt(ANALYZE_PROMPT).replace("{schema}", json.dumps(schema))
        payload: dict[str, object] = {
            "model": self._settings.ollama_model,
            "stream": False,
            "think": False,
            "format": schema,
            "options": {"temperature": 0},
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [base64.b64encode(image).decode()],
                }
            ],
        }
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return DocumentAnalysis.model_validate_json(await self._chat(payload))
            except ValidationError:
                logger.warning("analyze: invalid model output (attempt %d)", attempt)
            except (httpx.HTTPError, KeyError, ValueError) as error:
                logger.warning("analyze: model call failed (%s)", type(error).__name__)
                break
        return unreadable_result()


def get_llm() -> OllamaClient:
    return OllamaClient(get_settings())
