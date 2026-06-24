"""Tests for context types."""
from __future__ import annotations

from typing import Any

from moonlygram.ext import (
    Application,
    CallbackContext,
    ContextTypes,
    MessageHandler,
    filters,
)
from conftest import (
    _msg,
    _update,
    fake_bot,
)


class _MyContext(CallbackContext):
    pass


class _Store(dict):
    pass


async def test_context_types_uses_custom_context_class():
    bot, _ = fake_bot()
    app = Application(bot, context_types=ContextTypes(context=_MyContext))
    seen: list[Any] = []

    async def handler(update, context):
        seen.append(context)

    app.add_handler(MessageHandler(filters.all, handler))
    await app.process_update(_update(_msg("hi", from_id=5)))

    assert isinstance(seen[0], _MyContext)


async def test_context_types_custom_data_factories():
    bot, _ = fake_bot()
    app = Application(
        bot,
        context_types=ContextTypes(
            bot_data=_Store, chat_data=_Store, user_data=_Store
        ),
    )
    assert isinstance(app.bot_data, _Store)

    captured: list[Any] = []

    async def handler(update, context):
        captured.append((context.chat_data, context.user_data))

    app.add_handler(MessageHandler(filters.all, handler))
    await app.process_update(_update(_msg("hi", from_id=5)))

    chat_data, user_data = captured[0]
    assert isinstance(chat_data, _Store)
    assert isinstance(user_data, _Store)
