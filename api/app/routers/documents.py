from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlmodel import Session, col, select

from app.calendar import build_reminder
from app.config import Settings, get_settings
from app.db import get_session
from app.i18n import DEFAULT_LANG, LANGUAGES, Lang
from app.llm import OllamaClient, get_llm
from app.models import Document
from app.schemas import DocumentRead
from app.security import require_access_code
from app.uploads import read_image

router = APIRouter(prefix="/documents", dependencies=[Depends(require_access_code)])


@router.post("/analyze")
async def analyze_document(
    image: Annotated[UploadFile, File()],
    settings: Annotated[Settings, Depends(get_settings)],
    llm: Annotated[OllamaClient, Depends(get_llm)],
    session: Annotated[Session, Depends(get_session)],
    lang: Annotated[Lang, Query()] = DEFAULT_LANG,
) -> DocumentRead:
    data = await read_image(image, settings.max_image_bytes)
    analysis = await llm.analyze_document(data, lang)
    del data  # the photo is never stored

    if analysis.confidence == "low":
        # Unreadable or unsure: nothing worth keeping in her history.
        return DocumentRead(**analysis.model_dump(), id=None, created_at=None)

    document = Document(**analysis.model_dump())
    session.add(document)
    session.commit()
    session.refresh(document)
    return DocumentRead.model_validate(document, from_attributes=True)


@router.get("")
def list_documents(session: Annotated[Session, Depends(get_session)]) -> list[DocumentRead]:
    documents = session.exec(select(Document).order_by(col(Document.created_at).desc())).all()
    return [DocumentRead.model_validate(d, from_attributes=True) for d in documents]


def _get_or_404(session: Session, document_id: int) -> Document:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No encontramos ese papel.")
    return document


@router.get("/{document_id}")
def get_document(
    document_id: int, session: Annotated[Session, Depends(get_session)]
) -> DocumentRead:
    return DocumentRead.model_validate(_get_or_404(session, document_id), from_attributes=True)


@router.get("/{document_id}/reminder.ics")
def get_reminder(
    document_id: int,
    session: Annotated[Session, Depends(get_session)],
    lang: Annotated[Lang, Query()] = DEFAULT_LANG,
) -> Response:
    document = _get_or_404(session, document_id)
    if document.deadline is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Este papel no tiene fecha límite.")
    filename = LANGUAGES[lang].reminder_filename.format(id=document.id)
    return Response(
        content=build_reminder(document, lang),
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
