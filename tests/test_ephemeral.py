"""Tests for ephemeral messages (Bot API 10.2, reshaped in 10.3)."""
from __future__ import annotations

from moonlygram import (
    BotCommand,
    EphemeralMessageParameters,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
    ReplyParameters,
)
from conftest import (
    _MESSAGE_DICT,
    fake_bot,
)


async def test_send_message_carries_ephemeral_params():
    bot, session = fake_bot(_MESSAGE_DICT)
    await bot.send_message(
        1,
        "hi",
        ephemeral_message_parameters=EphemeralMessageParameters(
            receiver_user_id=99, callback_query_id="cb"
        ),
        reply_parameters=ReplyParameters(ephemeral_message_id=7),
    )
    method, params = session.calls[0]
    assert method == "sendMessage"
    assert params["ephemeral_message_parameters"] == {
        "receiver_user_id": 99,
        "callback_query_id": "cb",
    }
    assert params["reply_parameters"] == {"ephemeral_message_id": 7}


async def test_replace_callback_query_message_reaches_the_wire():
    bot, session = fake_bot(_MESSAGE_DICT)
    await bot.send_photo(
        1,
        "file123",
        ephemeral_message_parameters=EphemeralMessageParameters(
            receiver_user_id=99,
            callback_query_id="cb",
            replace_callback_query_message=True,
        ),
    )
    _, params = session.calls[0]
    assert params["ephemeral_message_parameters"]["replace_callback_query_message"]


async def test_send_rich_message_takes_ephemeral_parameters():
    bot, session = fake_bot(_MESSAGE_DICT)
    await bot.send_rich_message(
        1,
        html="<b>hi</b>",
        ephemeral_message_parameters=EphemeralMessageParameters(receiver_user_id=99),
    )
    method, params = session.calls[0]
    assert method == "sendRichMessage"
    assert params["ephemeral_message_parameters"] == {"receiver_user_id": 99}


def test_ephemeral_message_parameters_drops_unset_fields():
    assert EphemeralMessageParameters(9).to_dict() == {"receiver_user_id": 9}


def test_reply_parameters_drops_unset_fields():
    assert ReplyParameters(message_id=3, quote="hi").to_dict() == {
        "message_id": 3,
        "quote": "hi",
    }


async def test_edit_ephemeral_message_text():
    bot, session = fake_bot(True)
    result = await bot.edit_ephemeral_message_text(1, 99, 7, "new")
    assert result is True
    assert session.calls == [
        (
            "editEphemeralMessageText",
            {
                "chat_id": 1,
                "receiver_user_id": 99,
                "ephemeral_message_id": 7,
                "text": "new",
            },
        )
    ]


async def test_edit_ephemeral_message_media_serializes_media():
    bot, session = fake_bot(True)
    ok = await bot.edit_ephemeral_message_media(1, 99, 7, InputMediaPhoto("file123"))
    assert ok is True
    method, params = session.calls[0]
    assert method == "editEphemeralMessageMedia"
    assert params["media"] == {"type": "photo", "media": "file123"}
    assert params["receiver_user_id"] == 99
    assert params["ephemeral_message_id"] == 7


async def test_edit_ephemeral_message_caption_above_media():
    bot, session = fake_bot(True)
    ok = await bot.edit_ephemeral_message_caption(
        1, 99, 7, caption="c", show_caption_above_media=True
    )
    assert ok is True
    _, params = session.calls[0]
    assert params["show_caption_above_media"] is True


async def test_edit_ephemeral_rich_message_text():
    bot, session = fake_bot(True)
    ok = await bot.edit_ephemeral_rich_message_text(1, 99, 7, html="<b>hi</b>")
    assert ok is True
    method, params = session.calls[0]
    assert method == "editEphemeralMessageText"
    assert params["receiver_user_id"] == 99
    assert params["ephemeral_message_id"] == 7
    assert params["rich_message"] == {"html": "<b>hi</b>"}


async def test_edit_ephemeral_message_caption():
    bot, session = fake_bot(True)
    ok = await bot.edit_ephemeral_message_caption(1, 99, 7, caption="c")
    assert ok is True
    assert session.calls == [
        (
            "editEphemeralMessageCaption",
            {
                "chat_id": 1,
                "receiver_user_id": 99,
                "ephemeral_message_id": 7,
                "caption": "c",
            },
        )
    ]


async def test_edit_ephemeral_message_reply_markup():
    bot, session = fake_bot(True)
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("x", callback_data="y")]])
    ok = await bot.edit_ephemeral_message_reply_markup(1, 99, 7, reply_markup=markup)
    assert ok is True
    method, params = session.calls[0]
    assert method == "editEphemeralMessageReplyMarkup"
    assert params["reply_markup"] == {
        "inline_keyboard": [[{"text": "x", "callback_data": "y"}]]
    }


async def test_delete_ephemeral_message():
    bot, session = fake_bot(True)
    ok = await bot.delete_ephemeral_message(1, 99, 7)
    assert ok is True
    assert session.calls == [
        (
            "deleteEphemeralMessage",
            {"chat_id": 1, "receiver_user_id": 99, "ephemeral_message_id": 7},
        )
    ]


def test_message_parses_ephemeral_fields():
    msg = Message.from_dict(
        {
            "message_id": 5,
            "chat": {"id": 1, "type": "supergroup"},
            "ephemeral_message_id": 77,
            "receiver_user": {"id": 42, "is_bot": False, "first_name": "R"},
        }
    )
    assert msg.ephemeral_message_id == 77
    assert msg.receiver_user is not None
    assert msg.receiver_user.id == 42


def test_bot_command_is_ephemeral_roundtrip():
    cmd = BotCommand("start", "Start", is_ephemeral=True)
    assert cmd.to_dict() == {
        "command": "start",
        "description": "Start",
        "is_ephemeral": True,
    }
    parsed = BotCommand.from_dict(
        {"command": "a", "description": "b", "is_ephemeral": True}
    )
    assert parsed.is_ephemeral is True
    # The field is omitted when unset, keeping existing payloads unchanged.
    assert BotCommand("a", "b").to_dict() == {"command": "a", "description": "b"}
