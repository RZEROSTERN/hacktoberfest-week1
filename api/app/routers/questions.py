from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from sqlmodel import Session

from app.config import Settings, get_settings
from app.db import get_session
from app.i18n import DEFAULT_LANG, LANGUAGES, Lang
from app.llm import OllamaClient, get_llm
from app.models import Document
from app.schemas import VoiceAnswerRead
from app.security import require_access_code
from app.transcribe import Transcriber, TranscriptionError, get_transcriber
from app.uploads import read_audio

router = APIRouter(prefix="/questions", dependencies=[Depends(require_access_code)])


@router.post("/voice")
async def ask_by_voice(
    audio: Annotated[UploadFile, File()],
    settings: Annotated[Settings, Depends(get_settings)],
    llm: Annotated[OllamaClient, Depends(get_llm)],
    transcriber: Annotated[Transcriber, Depends(get_transcriber)],
    session: Annotated[Session, Depends(get_session)],
    document_id: Annotated[int | None, Form()] = None,
    lang: Annotated[Lang, Query()] = DEFAULT_LANG,
) -> VoiceAnswerRead:
    document: Document | None = None
    if document_id is not None:
        document = session.get(Document, document_id)
        if document is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No encontramos ese papel.")

    data = await read_audio(audio, settings.max_audio_bytes)
    try:
        question = await run_in_threadpool(transcriber.transcribe, data, lang)
    except TranscriptionError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "No pude oír la grabación. Intente de nuevo."
        ) from None
    finally:
        del data  # the recording is never stored

    if not question:
        return VoiceAnswerRead(
            question="",
            answer=LANGUAGES[lang].not_heard,
            confidence="low",
            document_id=document_id,
        )

    answer = await llm.answer_question(question, document, lang)
    return VoiceAnswerRead(**answer.model_dump(), question=question, document_id=document_id)
