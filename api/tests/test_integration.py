"""Hits the real Ollama model. Run with: uv run pytest -m integration"""

import pytest

from app.config import get_settings
from app.llm import OllamaClient
from app.transcribe import get_transcriber
from tests.conftest import SAMPLES


@pytest.mark.integration
async def test_telmex_sample_amount_and_no_invented_deadline() -> None:
    image = (SAMPLES / "telmex_sample.png").read_bytes()
    result = await OllamaClient(get_settings()).analyze_document(image)

    assert result.confidence != "low"
    assert result.amount_due == 2798.0
    assert result.deadline is None  # the bill says "INMEDIATO", not a date
    assert result.is_suspicious is False


@pytest.mark.integration
def test_spanish_voice_sample_is_transcribed_in_memory() -> None:
    audio = (SAMPLES / "question_telmex.m4a").read_bytes()
    text = get_transcriber().transcribe(audio, "es").lower()
    assert "pagar" in text and "recibo" in text


@pytest.mark.integration
async def test_telmex_sample_in_english_keeps_the_same_facts() -> None:
    image = (SAMPLES / "telmex_sample.png").read_bytes()
    result = await OllamaClient(get_settings()).analyze_document(image, "en")

    assert result.confidence != "low"
    assert result.amount_due == 2798.0
    assert result.deadline is None
    assert "pay" in result.explanation.lower()  # written in English, not Spanish


@pytest.mark.integration
def test_english_voice_sample_is_transcribed_in_memory() -> None:
    audio = (SAMPLES / "question_telmex_en.m4a").read_bytes()
    text = get_transcriber().transcribe(audio, "en").lower()
    assert "pay" in text and "bill" in text
