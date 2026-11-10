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


# --- Bot API 10.4: a callback query is enough to name the recipient --------


def test_parameters_accept_a_callback_query_alone():
    """Before 10.4 a receiver_user_id was required even when answering a
    button press, which a bot in a chat it knows no user ids for cannot give."""
    params = EphemeralMessageParameters(callback_query_id="cb")
    assert params.to_dict() == {"callback_query_id": "cb"}
    assert params.receiver_user_id is None


def test_parameters_naming_nobody_are_refused():
    import pytest

    with pytest.raises(ValueError, match="whole chat"):
        EphemeralMessageParameters()


async def test_send_message_without_a_chat_id_answers_the_query():
    """Answering a callback query ephemerally needs no chat: passing None
    leaves chat_id out of the payload rather than sending a null."""
    bot, session = fake_bot(_MESSAGE_DICT)
    await bot.send_message(
        None,
        "Only you can see this.",
        ephemeral_message_parameters=EphemeralMessageParameters(
            callback_query_id="cb"
        ),
    )
    method, params = session.calls[0]
    assert method == "sendMessage"
    assert "chat_id" not in params
    assert params["ephemeral_message_parameters"] == {"callback_query_id": "cb"}


async def test_every_ephemeral_capable_sender_takes_a_null_chat_id():
    """The spec made chat_id optional on fourteen send methods at once, so
    check the shape holds across the media ones rather than only sendMessage."""
    cases = [
        ("send_photo", ("file123",), "sendPhoto"),
        ("send_document", ("file123",), "sendDocument"),
        ("send_video", ("file123",), "sendVideo"),
        ("send_animation", ("file123",), "sendAnimation"),
        ("send_audio", ("file123",), "sendAudio"),
        ("send_voice", ("file123",), "sendVoice"),
        ("send_video_note", ("file123",), "sendVideoNote"),
        ("send_sticker", ("file123",), "sendSticker"),
        ("send_contact", ("+100", "A"), "sendContact"),
        ("send_location", (1.0, 2.0), "sendLocation"),
        ("send_venue", (1.0, 2.0, "T", "A"), "sendVenue"),
    ]
    for attr, args, method_name in cases:
        bot, session = fake_bot(_MESSAGE_DICT)
        await getattr(bot, attr)(
            None,
            *args,
            ephemeral_message_parameters=EphemeralMessageParameters(
                callback_query_id="cb"
            ),
        )
        method, params = session.calls[0]
        assert method == method_name
        assert "chat_id" not in params, f"{attr} still sent a chat_id"


async def test_send_rich_message_also_answers_a_query_without_a_chat():
    bot, session = fake_bot(_MESSAGE_DICT)
    await bot.send_rich_message(
        None,
        html="<b>hi</b>",
        ephemeral_message_parameters=EphemeralMessageParameters(
            callback_query_id="cb"
        ),
    )
    method, params = session.calls[0]
    assert method == "sendRichMessage"
    assert "chat_id" not in params


async def test_a_receiver_still_works_on_its_own():
    """The 10.3 spelling is untouched: widening the type broke no caller."""
    bot, session = fake_bot(_MESSAGE_DICT)
    await bot.send_message(
        1,
        "hi",
        ephemeral_message_parameters=EphemeralMessageParameters(receiver_user_id=99),
    )
    _, params = session.calls[0]
    assert params["chat_id"] == 1
    assert params["ephemeral_message_parameters"] == {"receiver_user_id": 99}
