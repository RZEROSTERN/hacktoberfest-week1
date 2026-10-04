from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel import Session

from app.config import Settings, get_settings
from app.db import get_session
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
) -> DocumentRead:
    data = await read_image(image, settings.max_image_bytes)
    analysis = await llm.analyze_document(data)
    del data  # the photo is never stored

    if analysis.confidence == "low":
        # Unreadable or unsure: nothing worth keeping in her history.
        return DocumentRead(**analysis.model_dump(), id=None, created_at=None)

    document = Document(**analysis.model_dump())
    session.add(document)
    session.commit()
    session.refresh(document)
    return DocumentRead.model_validate(document, from_attributes=True)
