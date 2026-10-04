"""Hits the real Ollama model. Run with: uv run pytest -m integration"""

import pytest

from app.config import get_settings
from app.llm import OllamaClient
from tests.conftest import SAMPLES


@pytest.mark.integration
async def test_telmex_sample_amount_and_no_invented_deadline() -> None:
    image = (SAMPLES / "telmex_sample.png").read_bytes()
    result = await OllamaClient(get_settings()).analyze_document(image)

    assert result.confidence != "low"
    assert result.amount_due == 2798.0
    assert result.deadline is None  # the bill says "INMEDIATO", not a date
    assert result.is_suspicious is False
