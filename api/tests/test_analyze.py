from datetime import date

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.db import get_engine
from app.i18n import Lang
from app.llm import get_llm, unreadable_result
from app.main import app
from app.models import Document
from app.schemas import DocumentAnalysis
from tests.conftest import AUTH

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
TELMEX = DocumentAnalysis(
    document_type="Recibo de Telmex",
    issuer="TELMEX",
    deadline=date(2026, 10, 18),
    amount_due=2798.0,
    required_actions=["Pagar el total de $2,798.00."],
    is_suspicious=False,
    fraud_reason=None,
    confidence="high",
    explanation="Es su recibo de teléfono.",
)


class FakeLLM:
    def __init__(self, result: DocumentAnalysis):
        self.result = result
        self.calls = 0
        self.langs: list[Lang] = []

    async def analyze_document(self, image: bytes, lang: Lang = "es") -> DocumentAnalysis:
        self.calls += 1
        self.langs.append(lang)
        return self.result


def use_llm(result: DocumentAnalysis) -> FakeLLM:
    fake = FakeLLM(result)
    app.dependency_overrides[get_llm] = lambda: fake
    return fake


def post_image(
    client: TestClient,
    data: bytes = PNG,
    content_type: str = "image/png",
    headers: dict[str, str] = AUTH,
    params: dict[str, str] | None = None,
) -> httpx.Response:
    response: httpx.Response = client.post(
        "/documents/analyze",
        params=params,
        files={"image": ("photo.png", data, content_type)},
        headers=headers,
    )
    return response


def test_analyze_returns_and_saves_structured_data(client: TestClient) -> None:
    use_llm(TELMEX)
    response = post_image(client)

    assert response.status_code == 200
    body = response.json()
    assert body["amount_due"] == 2798.0
    assert body["deadline"] == "2026-10-18"
    assert body["id"] is not None
    with Session(get_engine()) as session:
        saved = session.exec(select(Document)).one()
    assert saved.issuer == "TELMEX"
    assert saved.required_actions == ["Pagar el total de $2,798.00."]


def test_low_confidence_result_is_returned_but_not_saved(client: TestClient) -> None:
    use_llm(unreadable_result())
    response = post_image(client)

    assert response.status_code == 200
    assert response.json()["confidence"] == "low"
    assert response.json()["id"] is None
    with Session(get_engine()) as session:
        assert session.exec(select(Document)).all() == []


def test_rejects_missing_or_wrong_access_code(client: TestClient) -> None:
    fake = use_llm(TELMEX)
    assert post_image(client, headers={}).status_code == 401
    assert post_image(client, headers={"X-Access-Code": "nope"}).status_code == 401
    assert fake.calls == 0


def test_rejects_unsupported_type_before_calling_model(client: TestClient) -> None:
    fake = use_llm(TELMEX)
    assert post_image(client, b"%PDF-1.7", "application/pdf").status_code == 415
    assert post_image(client, b"not really a png", "image/png").status_code == 415
    assert fake.calls == 0


def test_rejects_oversized_image(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "max_image_bytes", 32)
    fake = use_llm(TELMEX)
    assert post_image(client).status_code == 413
    assert fake.calls == 0


def test_language_defaults_to_spanish_and_follows_the_lang_parameter(client: TestClient) -> None:
    fake = use_llm(TELMEX)
    assert post_image(client).status_code == 200
    assert post_image(client, params={"lang": "en"}).status_code == 200
    assert fake.langs == ["es", "en"]


def test_unsupported_language_is_rejected_before_calling_model(client: TestClient) -> None:
    fake = use_llm(TELMEX)
    assert post_image(client, params={"lang": "fr"}).status_code == 422
    assert fake.calls == 0
