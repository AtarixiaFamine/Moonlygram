"""Tests for bound-object reply shortcuts."""
from __future__ import annotations

import pytest

from moonlygram import (
    CallbackQuery,
    Message,
)
from moonlygram.ext import (
    Application,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from moonlygram.types import Update
from conftest import (
    _MESSAGE_DICT,
    fake_bot,
)


async def test_shortcut_raises_when_unbound():
    msg = Message.from_dict(_MESSAGE_DICT)
    with pytest.raises(RuntimeError):
        await msg.reply_text("hi")


async def test_message_reply_text_shortcut():
    bot, session = fake_bot(_MESSAGE_DICT)
    app = Application(bot)

    async def echo(update, context):
        await update.message.reply_text("pong")

    app.add_handler(MessageHandler(filters.text, echo))
    await app.process_update(Update.from_dict({"update_id": 1, "message": dict(_MESSAGE_DICT, text="ping")}))

    assert session.calls == [("sendMessage", {"chat_id": 1, "text": "pong"})]


async def test_message_edit_and_delete_shortcuts():
    bot, session = fake_bot(_MESSAGE_DICT)
    app = Application(bot)

    async def handler(update, context):
        await update.message.edit_text("new")
        await update.message.delete()

    app.add_handler(MessageHandler(filters.all, handler))
    await app.process_update(
        Update.from_dict({"update_id": 1, "message": dict(_MESSAGE_DICT, message_id=77, text="x")})
    )

    assert session.calls[0] == ("editMessageText", {"text": "new", "chat_id": 1, "message_id": 77})
    assert session.calls[1] == ("deleteMessage", {"chat_id": 1, "message_id": 77})


async def test_callback_query_answer_shortcut():
    bot, session = fake_bot(True)
    app = Application(bot)

    async def on_cb(update, context):
        await update.callback_query.answer("done", show_alert=True)

    app.add_handler(CallbackQueryHandler(on_cb))
    cq = {"id": "q9", "from": {"id": 2, "is_bot": False, "first_name": "A"}, "data": "x"}
    await app.process_update(Update(update_id=1, callback_query=CallbackQuery.from_dict(cq)))

    assert session.calls == [
        ("answerCallbackQuery", {"callback_query_id": "q9", "text": "done", "show_alert": True})
    ]


async def test_user_and_chat_send_shortcuts():
    bot, session = fake_bot(_MESSAGE_DICT)
    app = Application(bot)

    async def handler(update, context):
        await update.message.from_user.send_message("dm")
        await update.message.chat.send_message("to chat")

    app.add_handler(MessageHandler(filters.all, handler))
    raw = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "chat": {"id": 100, "type": "private"},
            "from": {"id": 200, "is_bot": False, "first_name": "U"},
            "text": "x",
        },
    }
    await app.process_update(Update.from_dict(raw))

    assert session.calls[0] == ("sendMessage", {"chat_id": 200, "text": "dm"})
    assert session.calls[1] == ("sendMessage", {"chat_id": 100, "text": "to chat"})
