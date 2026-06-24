"""Tests for the typed error hierarchy."""
from __future__ import annotations

import httpx
import pytest

from moonlygram import (
    APIError,
    BadRequest,
    ChatMigrated,
    Conflict,
    FloodWait,
    Forbidden,
    InvalidToken,
    NetworkError,
    NotFound,
    TimedOut,
    Unauthorized,
)
from moonlygram.session import Session
from conftest import (
    mock_bot,
)


def _error_response(code, description, parameters=None):
    """An httpx handler that replies with a Bot API ok: false envelope."""

    def handler(request):
        body = {"ok": False, "error_code": code, "description": description}
        if parameters is not None:
            body["parameters"] = parameters
        return httpx.Response(code if code < 600 else 200, json=body)

    return handler


@pytest.mark.parametrize(
    "code, expected",
    [
        (400, BadRequest),
        (401, Unauthorized),
        (403, Forbidden),
        (404, NotFound),
        (409, Conflict),
        (500, APIError),
    ],
)
async def test_status_codes_map_to_typed_errors(code, expected):
    bot = mock_bot(_error_response(code, "nope"))
    with pytest.raises(expected) as exc:
        await bot.get_me()
    assert exc.value.error_code == code
    assert exc.value.method == "getMe"
    assert isinstance(exc.value, APIError)


async def test_flood_wait_reads_retry_after():
    bot = mock_bot(_error_response(429, "slow down", {"retry_after": 7}))
    with pytest.raises(FloodWait) as exc:
        await bot.get_me()
    assert exc.value.retry_after == 7


async def test_chat_migrated_carries_new_chat_id():
    bot = mock_bot(_error_response(400, "migrated", {"migrate_to_chat_id": -100123}))
    with pytest.raises(ChatMigrated) as exc:
        await bot.get_me()
    assert exc.value.migrate_to_chat_id == -100123


async def test_transport_failure_becomes_network_error():
    def boom(request):
        raise httpx.ConnectError("refused")

    bot = mock_bot(boom)
    with pytest.raises(NetworkError):
        await bot.get_me()


async def test_timeout_becomes_timed_out():
    def slow(request):
        raise httpx.ReadTimeout("too slow")

    bot = mock_bot(slow)
    with pytest.raises(TimedOut):
        await bot.get_me()


def test_empty_token_raises_invalid_token():
    with pytest.raises(InvalidToken):
        Session("")
