"""Outgoing-request rate limiting.

A rate limiter sits in front of every Bot API call (Bot wraps session.call
through it) so a bot stays under Telegram's limits instead of relying on 429
retries alone. Plug one in with ApplicationBuilder.rate_limiter(...).

BaseRateLimiter is the interface; AIORateLimiter is a dependency-free default
that paces calls with a global limit plus a per-chat limit and retries on a
FloodWait. It mirrors python-telegram-bot's AIORateLimiter without the
APScheduler dependency.
"""
from __future__ import annotations

import asyncio
import time
from typing import Any, Awaitable, Callable, Optional

from ..errors import FloodWait

RequestCallback = Callable[[], Awaitable[Any]]


class BaseRateLimiter:
    """Interface for a limiter wrapping outgoing Bot API calls.

    Subclass and implement process_request; initialize / shutdown are optional
    lifecycle hooks the Application calls.
    """

    async def initialize(self) -> None:
        """Called once when the Application starts. Default does nothing."""

    async def shutdown(self) -> None:
        """Called once when the Application stops. Default does nothing."""

    async def process_request(
        self, callback: RequestCallback, *, chat_id: Optional[Any] = None
    ) -> Any:
        """Run callback() subject to the limit and return its result."""
        raise NotImplementedError


class _Spacer:
    """Hands out evenly spaced slots so calls stay under max_calls per period."""

    __slots__ = ("_min_interval", "_clock", "_next")

    def __init__(
        self, max_calls: float, period: float, clock: Callable[[], float]
    ) -> None:
        self._min_interval = period / max_calls
        self._clock = clock
        self._next = 0.0

    def reserve(self) -> float:
        """Reserve the next slot and return how long to wait before using it."""
        now = self._clock()
        start = now if now > self._next else self._next
        self._next = start + self._min_interval
        return start - now


class AIORateLimiter(BaseRateLimiter):
    """A token-bucket-style limiter: a global cap plus a per-chat cap.

    Rates are expressed as max_rate calls per time_period seconds; the limiter
    spaces calls evenly to honour them. On a FloodWait it waits the requested
    time and retries, up to max_retries.
    """

    def __init__(
        self,
        *,
        overall_max_rate: float = 30,
        overall_time_period: float = 1.0,
        per_chat_max_rate: float = 1,
        per_chat_time_period: float = 1.0,
        max_retries: int = 3,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._clock = clock
        self._sleep = sleep
        self.max_retries = max_retries
        self._overall = (
            _Spacer(overall_max_rate, overall_time_period, clock)
            if overall_max_rate
            else None
        )
        self._per_chat_max_rate = per_chat_max_rate
        self._per_chat_time_period = per_chat_time_period
        self._chat_spacers: dict[Any, _Spacer] = {}
        self._lock = asyncio.Lock()

    def _chat_spacer(self, chat_id: Any) -> _Spacer:
        spacer = self._chat_spacers.get(chat_id)
        if spacer is None:
            spacer = _Spacer(
                self._per_chat_max_rate, self._per_chat_time_period, self._clock
            )
            self._chat_spacers[chat_id] = spacer
        return spacer

    async def _reserve(self, chat_id: Optional[Any]) -> None:
        async with self._lock:
            delay = self._overall.reserve() if self._overall is not None else 0.0
            if chat_id is not None and self._per_chat_max_rate:
                delay = max(delay, self._chat_spacer(chat_id).reserve())
        if delay > 0:
            await self._sleep(delay)

    async def process_request(
        self, callback: RequestCallback, *, chat_id: Optional[Any] = None
    ) -> Any:
        retries = 0
        while True:
            await self._reserve(chat_id)
            try:
                return await callback()
            except FloodWait as exc:
                if retries >= self.max_retries:
                    raise
                retries += 1
                await self._sleep(exc.retry_after)
