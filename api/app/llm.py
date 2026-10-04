"""Async client for Gemma 4 via Ollama. Never logs prompts, images or model output."""

import base64
import json
import logging
from functools import lru_cache
from pathlib import Path

import httpx
from pydantic import BaseModel, ValidationError

from app.config import Settings, get_settings
from app.models import Document
from app.schemas import DocumentAnalysis, VoiceAnswer

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
ANALYZE_PROMPT = "analyze_v1.md"
QUESTIONS_PROMPT = "questions_v1.md"
MAX_ATTEMPTS = 2  # first try + one retry

# Only these structured fields are shared with the model as document context.
DOCUMENT_CONTEXT_FIELDS = {
    "document_type",
    "issuer",
    "deadline",
    "amount_due",
    "required_actions",
    "is_suspicious",
    "fraud_reason",
    "explanation",
}


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


def unanswered_result() -> VoiceAnswer:
    return VoiceAnswer(
        answer="Perdón, no pude contestar en este momento. ¿Me lo pregunta otra vez en un ratito?",
        confidence="low",
    )


class OllamaClient:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self._settings = settings
        self._transport = transport

    def _headers(self) -> dict[str, str]:
        key = self._settings.ollama_api_key.get_secret_value()
        return {"Authorization": f"Bearer {key}"} if key else {}

    async def _chat(self, payload: dict[str, object]) -> str:
        async with httpx.AsyncClient(
            base_url=self._settings.ollama_base_url,
            timeout=self._settings.ollama_timeout_seconds,
            transport=self._transport,
            headers=self._headers(),
        ) as client:
            response = await client.post("/api/chat", json=payload)
            response.raise_for_status()
            content: str = response.json()["message"]["content"]
            return content

    async def _structured[T: BaseModel](
        self, schema_model: type[T], prompt: str, images: list[bytes], fallback: T, task: str
    ) -> T:
        schema = schema_model.model_json_schema()
        # The prompt arrives fully rendered; user text inside it is never re-templated.
        message: dict[str, object] = {"role": "user", "content": prompt}
        if images:
            message["images"] = [base64.b64encode(image).decode() for image in images]
        payload: dict[str, object] = {
            "model": self._settings.ollama_model,
            "stream": False,
            "think": False,
            "format": schema,
            "options": {"temperature": 0},
            "messages": [message],
        }
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return schema_model.model_validate_json(await self._chat(payload))
            except ValidationError:
                logger.warning("%s: invalid model output (attempt %d)", task, attempt)
            except (httpx.HTTPError, KeyError, ValueError) as error:
                logger.warning("%s: model call failed (%s)", task, type(error).__name__)
                break
        return fallback

    async def analyze_document(self, image: bytes) -> DocumentAnalysis:
        prompt = load_prompt(ANALYZE_PROMPT).replace(
            "{schema}", json.dumps(DocumentAnalysis.model_json_schema())
        )
        return await self._structured(
            DocumentAnalysis, prompt, [image], unreadable_result(), "analyze"
        )

    async def answer_question(self, question: str, document: Document | None) -> VoiceAnswer:
        context = (
            document.model_dump_json(include=DOCUMENT_CONTEXT_FIELDS)
            if document is not None
            else "none"
        )
        # Fill {document} and {question} last so their text can't inject a {schema} marker.
        prompt = load_prompt(QUESTIONS_PROMPT).replace(
            "{schema}", json.dumps(VoiceAnswer.model_json_schema())
        )
        prompt = prompt.replace("{document}", context).replace("{question}", question)
        return await self._structured(VoiceAnswer, prompt, [], unanswered_result(), "question")


def get_llm() -> OllamaClient:
    return OllamaClient(get_settings())
