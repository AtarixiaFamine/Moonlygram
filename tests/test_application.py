"""Tests for Application lifecycle, polling, groups, and concurrency."""
from __future__ import annotations

import asyncio
from typing import Any

import pytest

from moonlygram import (
    Bot,
    NetworkError,
)
from moonlygram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from conftest import (
    FakeSession,
    _MESSAGE_DICT,
    _msg,
    _update,
    fake_bot,
)


class TestLifecycleAndPolling:
    async def test_initialize_caches_bot_user(self):
        bot, _ = fake_bot({"id": 7, "is_bot": True, "first_name": "Moon", "username": "moonbot"})
        app = Application(bot)
        await app.initialize()
        assert app.bot_user is not None
        assert app.bot_user.username == "moonbot"

    async def test_start_polling_dispatches_then_stops(self):
        # getUpdates returns one batch, then empties; a handler stops the loop.
        batch = [{"update_id": 5, "message": dict(_MESSAGE_DICT, text="/go")}]

        class PollSession(FakeSession):
            def __init__(self):
                super().__init__()
                self._sent = False

            async def call(self, method, /, **params):
                if method == "getUpdates":
                    if not self._sent:
                        self._sent = True
                        return batch
                    return []
                return await super().call(method, **params)

        bot = object.__new__(Bot)
        bot.session = PollSession()  # type: ignore[attr-defined]
        app = Application(bot, poll_timeout=0)
        seen: list[int] = []

        async def go(update, context):
            seen.append(update.update_id)
            app.stop()

        app.add_handler(CommandHandler("go", go))
        await asyncio.wait_for(app.start_polling(), timeout=2)

        assert seen == [5]
        assert app._running is False


class TestApplicationBuilder:
    def test_builder_requires_token(self):
        with pytest.raises(ValueError):
            Application.builder().build()

    async def test_builder_configures_polling(self):
        app = Application.builder().token("123:fake").poll_timeout(3).allowed_updates(["message"]).build()
        try:
            assert app._poll_timeout == 3
            assert app._allowed_updates == ["message"]
        finally:
            await app.shutdown()


class TestPollLoopResilience:
    async def test_poll_loop_retries_transient_error(self):
        batch = [{"update_id": 7, "message": dict(_MESSAGE_DICT, text="/go")}]

        class FlakySession(FakeSession):
            def __init__(self):
                super().__init__()
                self.attempts = 0

            async def call(self, method, /, **params):
                if method == "getUpdates":
                    self.attempts += 1
                    if self.attempts == 1:
                        # Session wraps transport failures into NetworkError before
                        # they reach the poll loop, so that is what it retries on.
                        raise NetworkError("boom")
                    return batch if self.attempts == 2 else []
                return await super().call(method, **params)

        bot = object.__new__(Bot)
        bot.session = FlakySession()  # type: ignore[attr-defined]
        app = Application(bot, poll_timeout=0)
        app._backoff_base = 0  # retry without a real delay
        seen: list[int] = []

        async def go(update, context):
            seen.append(update.update_id)
            app.stop()

        app.add_handler(CommandHandler("go", go))
        await asyncio.wait_for(app.start_polling(), timeout=2)

        assert seen == [7]
        assert bot.session.attempts >= 2


class TestErrorHandlers:
    async def test_error_handler_receives_exception(self):
        bot, _ = fake_bot()
        app = Application(bot)
        seen: dict[str, Any] = {}

        async def boom(update, context):
            raise RuntimeError("kaboom")

        async def on_error(update, context):
            seen["error"] = context.error
            seen["text"] = update.message.text

        app.add_handler(MessageHandler(filters.all, boom))
        app.add_error_handler(on_error)
        await app.process_update(_update(_msg("hi")))

        assert isinstance(seen["error"], RuntimeError)
        assert str(seen["error"]) == "kaboom"
        assert seen["text"] == "hi"

    async def test_error_handlers_all_run_and_dispatch_continues(self):
        bot, _ = fake_bot()
        app = Application(bot)
        calls: list[str] = []

        async def boom(update, context):
            raise ValueError("x")

        async def ok(update, context):
            calls.append("ok")

        async def err1(update, context):
            calls.append("err1")

        async def err2(update, context):
            calls.append("err2")

        app.add_handler(MessageHandler(filters.all, boom), group=0)
        app.add_handler(MessageHandler(filters.all, ok), group=1)
        app.add_error_handler(err1)
        app.add_error_handler(err2)
        await app.process_update(_update(_msg("hi")))

        assert calls == ["err1", "err2", "ok"]


class TestConcurrentDispatch:
    def test_concurrent_updates_normalizes_value(self):
        bot, _ = fake_bot()
        assert Application(bot, concurrent_updates=True)._concurrent_updates == 256
        assert Application(bot, concurrent_updates=3)._concurrent_updates == 3
        assert Application(bot)._concurrent_updates == 0

    async def test_non_blocking_handler_does_not_delay_later_groups(self):
        bot, _ = fake_bot()
        app = Application(bot)
        order: list[str] = []

        async def slow(update, context):
            await asyncio.sleep(0.05)
            order.append("slow")

        async def fast(update, context):
            order.append("fast")

        app.add_handler(MessageHandler(filters.all, slow, block=False), group=0)
        app.add_handler(MessageHandler(filters.all, fast), group=1)
        await app.process_update(_update(_msg("hi")))

        assert order == ["fast"]  # slow is detached and still running
        await asyncio.sleep(0.08)
        assert order == ["fast", "slow"]

    async def test_non_blocking_handler_error_routed_to_error_handler(self):
        bot, _ = fake_bot()
        app = Application(bot)
        errors: list[Any] = []

        async def boom(update, context):
            raise RuntimeError("bg boom")

        async def on_error(update, context):
            errors.append(context.error)

        app.add_handler(MessageHandler(filters.all, boom, block=False))
        app.add_error_handler(on_error)
        await app.process_update(_update(_msg("hi")))
        await asyncio.sleep(0.01)

        assert len(errors) == 1 and isinstance(errors[0], RuntimeError)

    async def test_sequential_consume_runs_one_update_at_a_time(self):
        bot, _ = fake_bot()
        app = Application(bot)  # concurrent_updates defaults off
        state = {"active": 0, "max": 0}

        async def handler(update, context):
            state["active"] += 1
            state["max"] = max(state["max"], state["active"])
            await asyncio.sleep(0.01)
            state["active"] -= 1

        app.add_handler(MessageHandler(filters.all, handler))
        queue: asyncio.Queue[Any] = asyncio.Queue()
        for _ in range(4):
            await queue.put(_update(_msg("hi")))
        await queue.put(None)
        await app._consume(queue)

        assert state["max"] == 1

    async def test_concurrent_consume_caps_at_limit(self):
        bot, _ = fake_bot()
        app = Application(bot, concurrent_updates=2)
        state = {"active": 0, "max": 0}

        async def handler(update, context):
            state["active"] += 1
            state["max"] = max(state["max"], state["active"])
            await asyncio.sleep(0.02)
            state["active"] -= 1

        app.add_handler(MessageHandler(filters.all, handler))
        queue: asyncio.Queue[Any] = asyncio.Queue()
        for _ in range(4):
            await queue.put(_update(_msg("hi")))
        await queue.put(None)
        await app._consume(queue)

        assert state["max"] == 2  # never more than the configured cap at once

    async def test_builder_threads_concurrent_updates(self):
        app = Application.builder().token("123:fake").concurrent_updates(4).build()
        try:
            assert app._concurrent_updates == 4
        finally:
            await app.shutdown()


class TestLifecycleHooks:
    async def test_run_polling_invokes_lifecycle_hooks(self):
        bot, _ = fake_bot({"id": 1, "is_bot": True, "first_name": "B", "username": "b"})
        order: list[str] = []

        async def pi(app):
            order.append("post_init")

        async def ps(app):
            order.append("post_stop")

        async def psd(app):
            order.append("post_shutdown")

        app = Application(bot, post_init=pi, post_stop=ps, post_shutdown=psd)

        async def fake_start_polling():
            order.append("poll")

        app.start_polling = fake_start_polling  # type: ignore[method-assign]
        await app._run_polling()

        assert order == ["post_init", "poll", "post_stop", "post_shutdown"]

    async def test_builder_wires_hooks_and_context_types(self):
        async def hook(app):
            pass

        ctypes = ContextTypes()
        app = (
            Application.builder()
            .token("1:abc")
            .post_init(hook)
            .post_stop(hook)
            .post_shutdown(hook)
            .context_types(ctypes)
            .build()
        )
        try:
            assert app.post_init is hook
            assert app.post_stop is hook
            assert app.post_shutdown is hook
            assert app.context_types is ctypes
        finally:
            await app.bot.close()
