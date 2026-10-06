"""Speech-to-text with faster-whisper. Audio stays in memory; transcripts are never logged."""

import io
import logging
from functools import cached_property, lru_cache

from faster_whisper import WhisperModel

from app.config import Settings, get_settings
from app.i18n import Lang

logger = logging.getLogger(__name__)


class TranscriptionError(Exception):
    """The audio could not be decoded or transcribed."""


class Transcriber:
    def __init__(self, settings: Settings):
        self._settings = settings

    @cached_property
    def _model(self) -> WhisperModel:
        return WhisperModel(
            self._settings.whisper_model,
            device="cpu",
            compute_type="int8",
            download_root=self._settings.whisper_model_dir,
        )

    def transcribe(self, audio: bytes, lang: Lang) -> str:
        """Blocking; call from a worker thread. Whisper is told which language to expect."""
        try:
            segments, _ = self._model.transcribe(
                io.BytesIO(audio), language=lang, vad_filter=True, beam_size=5
            )
            return " ".join(segment.text.strip() for segment in segments).strip()
        except Exception as error:  # PyAV/CTranslate2 raise many unrelated types
            logger.warning("transcribe: failed (%s)", type(error).__name__)
            raise TranscriptionError from error


@lru_cache
def get_transcriber() -> Transcriber:
    return Transcriber(get_settings())
