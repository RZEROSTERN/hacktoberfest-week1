import json
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.config import Settings
from app.db import get_engine
from app.i18n import Lang
from app.llm import OllamaClient, get_llm
from app.main import app
from app.models import Document
from app.schemas import VoiceAnswer
from app.transcribe import TranscriptionError, get_transcriber
from tests.conftest import AUTH

AUDIO = b"\x1aE\xdf\xa3" + b"\x00" * 64  # webm header bytes; content is never decoded here


class FakeTranscriber:
    def __init__(self, text: str | None):
        self.text = text
        self.langs: list[Lang] = []

    def transcribe(self, audio: bytes, lang: Lang) -> str:
        self.langs.append(lang)
        if self.text is None:
            raise TranscriptionError
        return self.text


class FakeLLM:
    def __init__(self, transcriber: FakeTranscriber) -> None:
        self.transcriber = transcriber
        self.calls: list[tuple[str, Document | None]] = []
        self.langs: list[Lang] = []

    async def answer_question(
        self, question: str, document: Document | None, lang: Lang = "es"
    ) -> VoiceAnswer:
        self.calls.append((question, document))
        self.langs.append(lang)
        return VoiceAnswer(answer="Debe pagar $2,798.00.", confidence="high")


def setup(transcript: str | None) -> FakeLLM:
    llm = FakeLLM(FakeTranscriber(transcript))
    app.dependency_overrides[get_llm] = lambda: llm
    app.dependency_overrides[get_transcriber] = lambda: llm.transcriber
    return llm


def ask(
    client: TestClient,
    content_type: str = "audio/webm;codecs=opus",
    data: dict[str, str] | None = None,
    headers: dict[str, str] = AUTH,
    params: dict[str, str] | None = None,
) -> httpx.Response:
    response: httpx.Response = client.post(
        "/questions/voice",
        params=params,
        files={"audio": ("pregunta.webm", AUDIO, content_type)},
        data=data or {},
        headers=headers,
    )
    return response


def test_answers_a_general_question(client: TestClient) -> None:
    llm = setup("¿Qué es el SAT?")
    response = ask(client)

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Debe pagar $2,798.00.",
        "confidence": "high",
        "question": "¿Qué es el SAT?",
        "document_id": None,
    }
    assert llm.calls == [("¿Qué es el SAT?", None)]


def test_answers_about_a_saved_document(client: TestClient) -> None:
    with Session(get_engine()) as session:
        document = Document(document_type="Recibo", confidence="high", explanation="x")
        session.add(document)
        session.commit()
        session.refresh(document)
    llm = setup("¿Cuánto pago?")

    response = ask(client, data={"document_id": str(document.id)})

    assert response.status_code == 200
    assert response.json()["document_id"] == document.id
    assert llm.calls[0][1] is not None and llm.calls[0][1].id == document.id


def test_unknown_document_is_404(client: TestClient) -> None:
    setup("hola")
    assert ask(client, data={"document_id": "999"}).status_code == 404


def test_silence_asks_to_repeat_without_calling_the_model(client: TestClient) -> None:
    llm = setup("")
    response = ask(client)
    assert response.json()["confidence"] == "low"
    assert "repetir" in response.json()["answer"]
    assert llm.calls == []


def test_undecodable_audio_is_422(client: TestClient) -> None:
    setup(None)
    assert ask(client).status_code == 422


def test_rejects_non_audio_and_missing_code(client: TestClient) -> None:
    llm = setup("hola")
    assert ask(client, content_type="image/png").status_code == 415
    assert ask(client, headers={}).status_code == 401
    assert llm.calls == []


def test_rejects_oversized_audio(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "max_audio_bytes", 16)
    setup("hola")
    assert ask(client).status_code == 413


def test_language_reaches_whisper_and_the_model(client: TestClient) -> None:
    llm = setup("What is the SAT?")
    assert ask(client).status_code == 200
    assert ask(client, params={"lang": "en"}).status_code == 200
    assert llm.transcriber.langs == ["es", "en"]
    assert llm.langs == ["es", "en"]


def test_silence_answer_follows_the_language(client: TestClient) -> None:
    setup("")
    answer = ask(client, params={"lang": "en"}).json()["answer"]
    assert "say it again" in answer
    assert "repetir" in ask(client).json()["answer"]


def test_unsupported_language_is_rejected(client: TestClient) -> None:
    llm = setup("hola")
    assert ask(client, params={"lang": "fr"}).status_code == 422
    assert llm.calls == []


async def test_question_prompt_shares_only_structured_fields() -> None:
    seen: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        reply = VoiceAnswer(answer="Sí.", confidence="high").model_dump_json()
        return httpx.Response(200, json={"message": {"content": reply}})

    llm = OllamaClient(Settings(), transport=httpx.MockTransport(handler))
    document = Document(id=5, document_type="Recibo", confidence="high", explanation="Es luz.")

    result = await llm.answer_question("¿Qué es? {schema}", document)

    assert result.answer == "Sí."
    message = seen[0]["messages"][0]
    assert "images" not in message
    assert '"document_type":"Recibo"' in message["content"]
    assert '"confidence"' not in message["content"].split("Her question:")[0].split("data")[1]
    assert "¿Qué es? {schema}" in message["content"]  # user text is not re-templated
