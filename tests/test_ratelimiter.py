"""Tests for the rate limiter."""
from __future__ import annotations

from typing import Any

import pytest

from moonlygram import (
    FloodWait,
)
from moonlygram.ext import (
    AIORateLimiter,
    BaseRateLimiter,
)
from conftest import (
    fake_bot,
)


def test_spacer_evenly_spaces_slots():
    from moonlygram.ext.ratelimiter import _Spacer

    spacer = _Spacer(2, 1.0, clock=lambda: 0.0)  # 2 per second -> 0.5s apart
    assert [spacer.reserve() for _ in range(3)] == [0.0, 0.5, 1.0]


async def test_rate_limiter_spaces_calls():
    sleeps: list[float] = []

    async def fake_sleep(delay):
        sleeps.append(delay)

    limiter = AIORateLimiter(
        overall_max_rate=2,
        overall_time_period=1.0,
        per_chat_max_rate=0,
        clock=lambda: 0.0,
        sleep=fake_sleep,
    )

    async def call():
        return "ok"

    results = [await limiter.process_request(call) for _ in range(3)]
    assert results == ["ok", "ok", "ok"]
    assert sleeps == [0.5, 1.0]  # the first call is free, then evenly spaced


async def test_rate_limiter_per_chat_is_independent():
    sleeps: list[float] = []

    async def fake_sleep(delay):
        sleeps.append(delay)

    limiter = AIORateLimiter(
        overall_max_rate=0,  # disable the global cap; test per-chat only
        per_chat_max_rate=1,
        per_chat_time_period=1.0,
        clock=lambda: 0.0,
        sleep=fake_sleep,
    )

    async def call():
        return "ok"

    await limiter.process_request(call, chat_id=1)  # chat 1, free
    await limiter.process_request(call, chat_id=2)  # chat 2, free (independent)
    await limiter.process_request(call, chat_id=1)  # chat 1 again, must wait
    assert sleeps == [1.0]


async def test_rate_limiter_retries_on_floodwait():
    sleeps: list[float] = []

    async def fake_sleep(delay):
        sleeps.append(delay)

    limiter = AIORateLimiter(
        overall_max_rate=0,
        per_chat_max_rate=0,
        max_retries=2,
        clock=lambda: 0.0,
        sleep=fake_sleep,
    )
    calls = {"n": 0}

    async def call():
        calls["n"] += 1
        if calls["n"] < 3:
            raise FloodWait(5, "slow down", "sendMessage")
        return "done"

    assert await limiter.process_request(call) == "done"
    assert calls["n"] == 3
    assert sleeps == [5, 5]


async def test_rate_limiter_gives_up_after_max_retries():
    async def fake_sleep(delay):
        pass

    limiter = AIORateLimiter(
        overall_max_rate=0,
        per_chat_max_rate=0,
        max_retries=1,
        clock=lambda: 0.0,
        sleep=fake_sleep,
    )

    async def call():
        raise FloodWait(1, "x", "sendMessage")

    with pytest.raises(FloodWait):
        await limiter.process_request(call)


async def test_bot_call_routes_through_rate_limiter():
    bot, session = fake_bot(
        {"message_id": 1, "chat": {"id": 5, "type": "private"}, "text": "hi"}
    )
    seen: dict[str, Any] = {}

    class RecordingLimiter(BaseRateLimiter):
        async def process_request(self, callback, *, chat_id=None):
            seen["chat_id"] = chat_id
            return await callback()

    bot.rate_limiter = RecordingLimiter()  # type: ignore[attr-defined]
    msg = await bot.send_message(5, "hi")
    assert msg.message_id == 1
    assert seen["chat_id"] == 5
    assert session.calls[0][0] == "sendMessage"
