"""Tests for arbitrary callback data."""
from __future__ import annotations

from typing import Any

from moonlygram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from moonlygram.ext import (
    Application,
    CallbackQueryHandler,
)
from moonlygram.types import Update
from conftest import (
    fake_bot,
)


def test_callback_data_cache_round_trip():
    from moonlygram.ext import CallbackDataCache

    cache = CallbackDataCache()
    obj = {"action": "delete", "id": 99}
    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Del", callback_data=obj),
                InlineKeyboardButton("Plain", callback_data="plain"),
            ]
        ]
    )
    rewritten = cache.process_keyboard(markup)
    assert rewritten is not markup
    token = rewritten.inline_keyboard[0][0].callback_data
    assert isinstance(token, str) and token != "plain"
    assert rewritten.inline_keyboard[0][1].callback_data == "plain"  # str untouched

    query = CallbackQuery.from_dict(
        {"id": "1", "from": {"id": 1, "is_bot": False, "first_name": "A"}, "data": token}
    )
    cache.process_callback_query(query)
    assert query.data == obj

    unknown = CallbackQuery.from_dict(
        {"id": "2", "from": {"id": 1, "is_bot": False, "first_name": "A"}, "data": "plain"}
    )
    cache.process_callback_query(unknown)
    assert unknown.data == "plain"  # not a known token: left as-is


def test_callback_data_cache_passes_through_other_markup():
    from moonlygram.ext import CallbackDataCache

    cache = CallbackDataCache()
    reply = ReplyKeyboardMarkup([[KeyboardButton("hi")]])
    assert cache.process_keyboard(reply) is reply
    all_strings = InlineKeyboardMarkup([[InlineKeyboardButton("x", callback_data="s")]])
    assert cache.process_keyboard(all_strings) is all_strings


def test_callback_data_cache_evicts_least_recently_used():
    from moonlygram.ext.callbackdata import CallbackDataCache, _MISSING

    cache = CallbackDataCache(maxsize=2)
    t1 = cache.put("a")
    t2 = cache.put("b")
    cache.put("c")  # over capacity: evict the oldest (t1)
    assert cache.get(t1) is _MISSING
    assert cache.get(t2) == "b"


async def test_arbitrary_callback_data_end_to_end():
    from moonlygram.ext import CallbackDataCache

    bot, session = fake_bot({"message_id": 1, "chat": {"id": 1, "type": "private"}})
    bot.callback_data_cache = CallbackDataCache()  # type: ignore[attr-defined]
    obj = ("vote", 7)
    await bot.send_message(
        1,
        "pick",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Vote", callback_data=obj)]]
        ),
    )
    sent_markup = session.calls[0][1]["reply_markup"]
    token = sent_markup["inline_keyboard"][0][0]["callback_data"]
    assert isinstance(token, str)

    app = Application(bot)
    seen: dict[str, Any] = {}

    async def on_cb(update, context):
        seen["data"] = update.callback_query.data

    app.add_handler(CallbackQueryHandler(on_cb))
    await app.process_update(
        Update(
            update_id=1,
            callback_query=CallbackQuery.from_dict(
                {
                    "id": "c",
                    "from": {"id": 1, "is_bot": False, "first_name": "A"},
                    "data": token,
                }
            ),
        )
    )
    assert seen["data"] == obj
