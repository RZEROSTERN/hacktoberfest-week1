from datetime import UTC, date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.calendar import _fold, build_reminder
from app.db import get_engine
from app.models import Document
from tests.conftest import AUTH


def add_document(**overrides: object) -> Document:
    fields: dict[str, object] = {
        "document_type": "Recibo de luz",
        "issuer": "CFE",
        "deadline": date(2026, 10, 18),
        "amount_due": 1482.5,
        "required_actions": ["Pagar en el OXXO, con el recibo en la mano."],
        "is_suspicious": False,
        "fraud_reason": None,
        "confidence": "high",
        "explanation": "Es su recibo de luz; debe pagar antes del 18 de octubre.",
    }
    fields.update(overrides)
    with Session(get_engine()) as session:
        document = Document.model_validate(fields)
        session.add(document)
        session.commit()
        session.refresh(document)
        return document


def test_history_lists_newest_first(client: TestClient) -> None:
    now = datetime.now(UTC)
    add_document(document_type="Viejo", created_at=now - timedelta(days=2))
    add_document(document_type="Nuevo", created_at=now)

    response = client.get("/documents", headers=AUTH)

    assert response.status_code == 200
    assert [d["document_type"] for d in response.json()] == ["Nuevo", "Viejo"]


def test_history_requires_access_code(client: TestClient) -> None:
    assert client.get("/documents").status_code == 401
    assert client.get("/documents/1").status_code == 401
    assert client.get("/documents/1/reminder.ics").status_code == 401


def test_get_document_and_404(client: TestClient) -> None:
    document = add_document()
    assert client.get(f"/documents/{document.id}", headers=AUTH).json()["issuer"] == "CFE"
    assert client.get("/documents/999", headers=AUTH).status_code == 404


def test_reminder_ics_download(client: TestClient) -> None:
    document = add_document()

    response = client.get(f"/documents/{document.id}/reminder.ics", headers=AUTH)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/calendar")
    assert "attachment" in response.headers["content-disposition"]
    body = response.text
    assert body.startswith("BEGIN:VCALENDAR\r\n") and body.endswith("END:VCALENDAR\r\n")
    assert "DTSTART;VALUE=DATE:20261018" in body
    assert "TRIGGER:-P3D" in body and "TRIGGER:-P1D" in body


def test_reminder_404_without_deadline(client: TestClient) -> None:
    document = add_document(deadline=None)
    assert client.get(f"/documents/{document.id}/reminder.ics", headers=AUTH).status_code == 404


def test_reminder_escapes_text_and_includes_amount() -> None:
    document = Document(
        id=7,
        document_type="Aviso; urgente, SAT",
        deadline=date(2026, 11, 2),
        amount_due=1234.5,
        required_actions=[],
        confidence="medium",
        explanation="Línea uno\nLínea dos",
    )
    unfolded = build_reminder(document).replace("\r\n ", "")
    assert "SUMMARY:Vence: Aviso\; urgente\\, SAT" in unfolded
    assert "Línea uno\\nLínea dos" in unfolded
    assert "$1\\,234.50 MXN" in unfolded


def test_long_lines_are_folded_at_75_octets() -> None:
    folded = _fold("DESCRIPTION:" + "ñ" * 100)
    assert all(len(line.encode()) <= 75 for line in folded.split("\r\n"))
    assert folded.replace("\r\n ", "") == "DESCRIPTION:" + "ñ" * 100
