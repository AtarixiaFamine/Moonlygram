"""Tests for handlers and dispatch."""
from __future__ import annotations

from typing import Any

from moonlygram import (
    CallbackQuery,
    Message,
)
from moonlygram.ext import (
    Application,
    ApplicationHandlerStop,
    CommandHandler,
    MessageHandler,
    PrefixHandler,
    TypeHandler,
    filters,
)
from moonlygram.types import Update
from conftest import (
    _msg,
    _update,
    fake_bot,
)


class TestHandlersAndDispatch:
    async def test_command_handler_sets_context_args(self):
        bot, _ = fake_bot()
        app = Application(bot)
        seen: dict[str, Any] = {}

        async def start(update, context):
            seen["args"] = context.args
            seen["bot"] = context.bot

        app.add_handler(CommandHandler("start", start))
        await app.process_update(_update(_msg("/start one two")))

        assert seen["args"] == ["one", "two"]
        assert seen["bot"] is bot

    async def test_message_handler_honors_filter(self):
        bot, _ = fake_bot()
        app = Application(bot)
        hits: list[str | None] = []

        async def echo(update, context):
            hits.append(update.message.text)

        app.add_handler(MessageHandler(filters.text, echo))
        await app.process_update(_update(_msg("hello")))
        await app.process_update(_update(_msg(None)))  # no text: filtered out

        assert hits == ["hello"]

    async def test_process_update_routes_to_matching_handler_only(self):
        bot, _ = fake_bot()
        app = Application(bot)
        called: list[str] = []

        async def on_start(update, context):
            called.append("start")

        async def on_help(update, context):
            called.append("help")

        app.add_handler(CommandHandler("start", on_start))
        app.add_handler(CommandHandler("help", on_help))
        await app.process_update(_update(_msg("/help")))

        assert called == ["help"]

    async def test_failing_handler_does_not_stop_dispatch(self):
        bot, _ = fake_bot()
        app = Application(bot)
        called: list[str] = []

        async def boom(update, context):
            raise RuntimeError("handler error")

        async def ok(update, context):
            called.append("ok")

        app.add_handler(MessageHandler(filters.all, boom), group=0)
        app.add_handler(MessageHandler(filters.all, ok), group=1)
        await app.process_update(_update(_msg("hi")))

        assert called == ["ok"]


class TestHandlerGroups:
    async def test_first_match_per_group_and_group_order(self):
        bot, _ = fake_bot()
        app = Application(bot)
        order: list[str] = []

        async def a(update, context):
            order.append("a")

        async def b(update, context):
            order.append("b")

        async def c(update, context):
            order.append("c")

        app.add_handler(MessageHandler(filters.all, a), group=0)
        app.add_handler(MessageHandler(filters.all, b), group=0)  # same group: skipped
        app.add_handler(MessageHandler(filters.all, c), group=1)  # next group: runs
        await app.process_update(_update(_msg("hi")))

        assert order == ["a", "c"]

    async def test_application_handler_stop_halts_processing(self):
        bot, _ = fake_bot()
        app = Application(bot)
        ran: list[str] = []

        async def stop_it(update, context):
            ran.append("g0")
            raise ApplicationHandlerStop

        async def later(update, context):
            ran.append("g1")

        app.add_handler(MessageHandler(filters.all, stop_it), group=0)
        app.add_handler(MessageHandler(filters.all, later), group=1)
        await app.process_update(_update(_msg("hi")))

        assert ran == ["g0"]

    async def test_type_handler_runs_for_every_update(self):
        bot, _ = fake_bot()
        app = Application(bot)
        seen: list[int] = []

        async def tap(update, context):
            seen.append(update.update_id)

        app.add_handler(TypeHandler(tap))
        cq = {"id": "1", "from": {"id": 1, "is_bot": False, "first_name": "A"}, "data": "x"}
        await app.process_update(Update(update_id=5, callback_query=CallbackQuery.from_dict(cq)))
        await app.process_update(_update(_msg("hi")))

        assert seen == [5, 1]

    async def test_prefix_handler(self):
        bot, _ = fake_bot()
        app = Application(bot)
        seen: list[list[str] | None] = []

        async def h(update, context):
            seen.append(context.args)

        app.add_handler(PrefixHandler("!", "ban", h))
        await app.process_update(_update(_msg("!ban alice 3")))
        await app.process_update(_update(_msg("/ban alice")))  # wrong prefix: no match

        assert seen == [["alice", "3"]]

    def test_user_and_chat_filters(self):
        m = _msg("hi", from_id=42)
        assert filters.user(42)(m)
        assert not filters.user(99)(m)
        assert filters.chat(1)(m)
        assert not filters.chat(2)(m)

    def test_caption_regex_filter(self):
        cap = Message.from_dict({"message_id": 1, "chat": {"id": 1, "type": "private"}, "caption": "invoice #42"})
        assert filters.caption_regex(r"#\d+")(cap)
        assert not filters.caption_regex(r"zzz")(cap)
