"""Tests for Bot API method wrappers, keyboards, and defaults."""
from __future__ import annotations

import pytest

from moonlygram import (
    BotDescription,
    BotName,
    BotShortDescription,
    CallbackQuery,
    Defaults,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    MessageId,
    ReplyKeyboardMarkup,
)
from moonlygram.ext import (
    Application,
    CallbackQueryHandler,
)
from moonlygram.types import Update
from conftest import (
    _MESSAGE_DICT,
    fake_bot,
)


class TestBotMethods:
    async def test_send_message_drops_none_params(self):
        bot, session = fake_bot(_MESSAGE_DICT)
        result = await bot.send_message(1, "hi")
        assert isinstance(result, Message)
        assert session.calls == [("sendMessage", {"chat_id": 1, "text": "hi"})]

    async def test_send_rich_message_requires_exactly_one_format(self):
        bot, _ = fake_bot()
        with pytest.raises(ValueError):
            await bot.send_rich_message(1, html="<p>x</p>", markdown="x")
        with pytest.raises(ValueError):
            await bot.send_rich_message(1)

    async def test_edit_message_text_parses_message(self):
        bot, session = fake_bot(_MESSAGE_DICT)
        result = await bot.edit_message_text("new", chat_id=1, message_id=10)
        assert isinstance(result, Message)
        assert session.calls == [
            ("editMessageText", {"text": "new", "chat_id": 1, "message_id": 10})
        ]

    async def test_edit_message_text_inline_returns_true(self):
        bot, _ = fake_bot(True)
        result = await bot.edit_message_text("new", inline_message_id="abc")
        assert result is True

    async def test_copy_message_returns_message_id(self):
        bot, session = fake_bot({"message_id": 42})
        result = await bot.copy_message(1, 2, 10)
        assert result == MessageId(message_id=42)
        assert session.calls == [
            ("copyMessage", {"chat_id": 1, "from_chat_id": 2, "message_id": 10})
        ]

    async def test_delete_message_returns_bool(self):
        bot, session = fake_bot(True)
        assert await bot.delete_message(1, 10) is True
        assert session.calls == [("deleteMessage", {"chat_id": 1, "message_id": 10})]

    async def test_send_chat_action_returns_bool(self):
        bot, session = fake_bot(True)
        assert await bot.send_chat_action(1, "typing") is True
        assert session.calls == [("sendChatAction", {"chat_id": 1, "action": "typing"})]


class TestCallbacksAndKeyboards:
    def test_inline_keyboard_to_dict(self):
        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Yes", callback_data="y"), InlineKeyboardButton("Docs", url="https://x")]]
        )
        assert markup.to_dict() == {
            "inline_keyboard": [
                [{"text": "Yes", "callback_data": "y"}, {"text": "Docs", "url": "https://x"}]
            ]
        }

    def test_reply_keyboard_to_dict(self):
        markup = ReplyKeyboardMarkup([[KeyboardButton("A"), KeyboardButton("B")]], resize_keyboard=True)
        assert markup.to_dict() == {
            "keyboard": [[{"text": "A"}, {"text": "B"}]],
            "resize_keyboard": True,
        }

    async def test_send_message_serializes_markup(self):
        bot, session = fake_bot(_MESSAGE_DICT)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Hi", callback_data="hi")]])
        await bot.send_message(1, "hi", reply_markup=markup)
        _, params = session.calls[0]
        assert params["reply_markup"] == {"inline_keyboard": [[{"text": "Hi", "callback_data": "hi"}]]}

    async def test_answer_callback_query(self):
        bot, session = fake_bot(True)
        assert await bot.answer_callback_query("q1", text="ok") is True
        assert session.calls == [
            ("answerCallbackQuery", {"callback_query_id": "q1", "text": "ok"})
        ]

    def test_update_parses_callback_query(self):
        raw = {
            "update_id": 9,
            "callback_query": {
                "id": "x",
                "from": {"id": 3, "is_bot": False, "first_name": "B"},
                "message": _MESSAGE_DICT,
                "data": "vote:yes",
            },
        }
        update = Update.from_dict(raw)
        assert update.callback_query is not None
        assert update.callback_query.data == "vote:yes"
        assert update.effective_user_id == 3
        assert update.effective_chat_id == 1

    async def test_callback_query_handler_honors_pattern(self):
        bot, _ = fake_bot()
        app = Application(bot)
        got: list[str | None] = []

        async def on_vote(update, context):
            got.append(update.callback_query.data)

        app.add_handler(CallbackQueryHandler(on_vote, pattern=r"^vote:"))
        base = {"id": "1", "from": {"id": 2, "is_bot": False, "first_name": "A"}}
        await app.process_update(Update(update_id=1, callback_query=CallbackQuery.from_dict(dict(base, data="vote:yes"))))
        await app.process_update(Update(update_id=2, callback_query=CallbackQuery.from_dict(dict(base, data="other"))))

        assert got == ["vote:yes"]


class TestEscapeHatchAndDefaults:
    async def test_bot_call_escape_hatch(self):
        bot, session = fake_bot({"ok": True})
        await bot.call("someNewMethod", chat_id=1, foo="bar")
        assert session.calls == [("someNewMethod", {"chat_id": 1, "foo": "bar"})]

    async def test_defaults_fill_unset_param(self):
        bot, session = fake_bot(_MESSAGE_DICT)
        bot.defaults = Defaults(parse_mode="HTML")  # type: ignore[attr-defined]
        await bot.send_message(1, "hi")
        _, params = session.calls[0]
        assert params["parse_mode"] == "HTML"

    async def test_defaults_do_not_override_explicit(self):
        bot, session = fake_bot(_MESSAGE_DICT)
        bot.defaults = Defaults(parse_mode="HTML")  # type: ignore[attr-defined]
        await bot.send_message(1, "hi", parse_mode="MarkdownV2")
        _, params = session.calls[0]
        assert params["parse_mode"] == "MarkdownV2"

    async def test_defaults_not_injected_when_param_absent(self):
        bot, session = fake_bot({"id": 1, "is_bot": True, "first_name": "B"})
        bot.defaults = Defaults(parse_mode="HTML")  # type: ignore[attr-defined]
        await bot.get_me()
        _, params = session.calls[0]
        assert "parse_mode" not in params


class TestBotConfiguration:
    async def test_set_my_name_and_short_description_params(self):
        bot, session = fake_bot(True)
        await bot.set_my_name(name="Moon", language_code="en")
        assert session.calls[0] == ("setMyName", {"name": "Moon", "language_code": "en"})

        await bot.set_my_short_description(short_description="hi")
        assert session.calls[1] == ("setMyShortDescription", {"short_description": "hi"})

    async def test_get_my_name_description_short_description_parse(self):
        bot, _ = fake_bot({"name": "Moon"})
        name = await bot.get_my_name()
        assert isinstance(name, BotName) and name.name == "Moon"

        bot2, _ = fake_bot({"description": "Full description"})
        description = await bot2.get_my_description()
        assert isinstance(description, BotDescription)
        assert description.description == "Full description"

        bot3, _ = fake_bot({"short_description": "Short"})
        short = await bot3.get_my_short_description()
        assert isinstance(short, BotShortDescription) and short.short_description == "Short"
