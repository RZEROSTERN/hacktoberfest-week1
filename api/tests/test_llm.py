import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest

from app.config import Settings
from app.llm import OllamaClient
from tests.test_analyze import TELMEX


def client_with(handler: Callable[[httpx.Request], httpx.Response]) -> OllamaClient:
    settings = Settings(ollama_base_url="http://ollama.test", ollama_timeout_seconds=1)
    return OllamaClient(settings, transport=httpx.MockTransport(handler))


def chat_reply(content: str) -> httpx.Response:
    return httpx.Response(200, json={"message": {"role": "assistant", "content": content}})


async def test_valid_output_is_parsed_and_request_is_well_formed() -> None:
    seen: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        return chat_reply(TELMEX.model_dump_json())

    result = await client_with(handler).analyze_document(b"img")

    assert result == TELMEX
    body = seen[0]
    assert body["think"] is False
    assert body["format"]["properties"]["amount_due"]
    assert body["messages"][0]["images"] == ["aW1n"]


async def test_invalid_output_is_retried_once() -> None:
    replies = iter([chat_reply('{"document_type": 1}'), chat_reply(TELMEX.model_dump_json())])
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return next(replies)

    assert await client_with(handler).analyze_document(b"img") == TELMEX
    assert calls == 2


async def test_two_invalid_outputs_give_low_confidence_instead_of_guessing() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return chat_reply("not json")

    result = await client_with(handler).analyze_document(b"img")
    assert calls == 2
    assert result.confidence == "low"
    assert result.amount_due is None and result.deadline is None


@pytest.mark.parametrize(
    "failure",
    [httpx.ConnectError("down"), httpx.ReadTimeout("slow")],
)
async def test_model_failure_never_raises(failure: Exception) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise failure

    result = await client_with(handler).analyze_document(b"img")
    assert result.confidence == "low"
