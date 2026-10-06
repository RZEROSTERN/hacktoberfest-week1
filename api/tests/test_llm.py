import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest
from pydantic import SecretStr

from app.config import Settings
from app.i18n import LANGUAGES, Lang
from app.llm import ANALYZE_PROMPT, QUESTIONS_PROMPT, OllamaClient, render_prompt
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


async def test_bearer_token_is_sent_only_when_configured() -> None:
    seen: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers.get("authorization"))
        return chat_reply(TELMEX.model_dump_json())

    transport = httpx.MockTransport(handler)
    await OllamaClient(Settings(), transport=transport).analyze_document(b"img")
    with_key = Settings(ollama_api_key=SecretStr("s3cret"))
    await OllamaClient(with_key, transport=transport).analyze_document(b"img")

    assert seen == [None, "Bearer s3cret"]


@pytest.mark.parametrize("name", [ANALYZE_PROMPT, QUESTIONS_PROMPT])
@pytest.mark.parametrize("lang", ["es", "en"])
def test_rendered_prompt_has_no_unfilled_language_markers(name: str, lang: Lang) -> None:
    prompt = render_prompt(name, lang)
    assert "{language_style}" not in prompt and "{language_note}" not in prompt
    assert LANGUAGES[lang].style in prompt


async def test_prompt_asks_for_the_requested_language() -> None:
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content)["messages"][0]["content"])
        return chat_reply(TELMEX.model_dump_json())

    llm = client_with(handler)
    await llm.analyze_document(b"img", "es")
    await llm.analyze_document(b"img", "en")

    assert 'Mexican Spanish ("usted")' in seen[0] and "plain English" not in seen[0]
    assert "plain English" in seen[1] and "Mexican Spanish" not in seen[1]
    assert "{schema}" not in seen[1]


async def test_failure_fallback_is_in_the_requested_language() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down")

    llm = client_with(handler)
    spanish = await llm.analyze_document(b"img")
    english = await llm.analyze_document(b"img", "en")

    assert spanish.document_type == "No se pudo leer"
    assert english.document_type == "Could not be read"
    assert english.confidence == "low"
    assert "another photo" in english.required_actions[0]
