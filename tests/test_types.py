"""Tests for received-type parsing completeness."""
from __future__ import annotations

from moonlygram import (
    Message,
    MessageOrigin,
    MessageReactionUpdated,
    ReactionTypeCustomEmoji,
    ReactionTypeEmoji,
    ReactionTypePaid,
)
from moonlygram.ext import (
    filters,
)
from conftest import (
    _FULL_MESSAGE_RAW,
    fake_bot,
)


def test_message_parses_completed_fields():
    msg = Message.from_dict(_FULL_MESSAGE_RAW)
    assert msg.date == 1000
    assert msg.edit_date == 1001
    assert msg.message_thread_id == 7
    assert msg.author_signature == "Admin"
    assert msg.has_protected_content is True
    assert msg.is_automatic_forward is True
    assert msg.via_bot is not None and msg.via_bot.id == 9
    assert msg.reply_to_message is not None
    assert msg.reply_to_message.text == "original"
    assert msg.reply_to_message.chat.id == 200
    assert [u.id for u in msg.new_chat_members] == [11, 12]
    assert msg.left_chat_member is not None and msg.left_chat_member.id == 13
    assert msg.pinned_message is not None and msg.pinned_message.text == "pinned"


def test_message_completed_fields_default_none():
    msg = Message.from_dict({"message_id": 1, "chat": {"id": 1, "type": "private"}})
    assert msg.date is None
    assert msg.reply_to_message is None
    assert msg.via_bot is None
    assert msg.forward_origin is None
    assert msg.new_chat_members is None


def test_message_forward_origin_variants():
    def origin(d):
        return Message.from_dict(
            {"message_id": 1, "chat": {"id": 1, "type": "private"}, "forward_origin": d}
        ).forward_origin

    user = origin(
        {"type": "user", "date": 1, "sender_user": {"id": 5, "is_bot": False, "first_name": "A"}}
    )
    assert isinstance(user, MessageOrigin)
    assert user.type == "user" and user.sender_user.id == 5

    hidden = origin({"type": "hidden_user", "date": 1, "sender_user_name": "Anon"})
    assert hidden.type == "hidden_user" and hidden.sender_user_name == "Anon"

    chat = origin(
        {"type": "chat", "date": 1, "sender_chat": {"id": -100, "type": "group"}, "author_signature": "S"}
    )
    assert chat.sender_chat.id == -100 and chat.author_signature == "S"

    channel = origin(
        {"type": "channel", "date": 1, "chat": {"id": -200, "type": "channel"}, "message_id": 8}
    )
    assert channel.chat.id == -200 and channel.message_id == 8


async def test_set_bot_binds_nested_message_objects():
    bot, session = fake_bot(
        result={"message_id": 99, "chat": {"id": 200, "type": "private"}}
    )
    msg = Message.from_dict(_FULL_MESSAGE_RAW)
    msg.set_bot(bot)

    # The replied-to message is bound: its shortcut routes to the replied chat.
    await msg.reply_to_message.reply_text("hi")
    method, params = session.calls[-1]
    assert method == "sendMessage" and params["chat_id"] == 200

    assert msg.via_bot._bot is bot
    assert msg.pinned_message._bot is bot
    assert msg.new_chat_members[0]._bot is bot
    assert msg.left_chat_member._bot is bot


async def test_set_message_reaction_serializes_custom_and_paid():
    bot, session = fake_bot()
    await bot.set_message_reaction(
        1, 5, reaction=[ReactionTypeCustomEmoji("123"), ReactionTypePaid()]
    )
    _, params = session.calls[-1]
    assert params["reaction"] == [
        {"type": "custom_emoji", "custom_emoji_id": "123"},
        {"type": "paid"},
    ]


def test_reaction_updated_parses_all_variants():
    raw = {
        "chat": {"id": 1, "type": "supergroup"},
        "message_id": 7,
        "user": {"id": 5, "is_bot": False, "first_name": "A"},
        "date": 0,
        "old_reaction": [],
        "new_reaction": [
            {"type": "emoji", "emoji": "\N{THUMBS UP SIGN}"},
            {"type": "custom_emoji", "custom_emoji_id": "99"},
            {"type": "paid"},
            {"type": "future_kind", "data": 1},
        ],
    }
    emoji, custom, paid, unknown = MessageReactionUpdated.from_dict(raw).new_reaction
    assert isinstance(emoji, ReactionTypeEmoji) and emoji.emoji == "\N{THUMBS UP SIGN}"
    assert isinstance(custom, ReactionTypeCustomEmoji) and custom.custom_emoji_id == "99"
    assert isinstance(paid, ReactionTypePaid)
    assert unknown == {"type": "future_kind", "data": 1}  # unknown kind kept raw


def test_reply_and_forwarded_filters():
    plain = Message.from_dict(
        {"message_id": 1, "chat": {"id": 1, "type": "private"}, "text": "hi"}
    )
    replied = Message.from_dict(_FULL_MESSAGE_RAW)
    forwarded = Message.from_dict(
        {
            "message_id": 2,
            "chat": {"id": 1, "type": "private"},
            "forward_origin": {"type": "hidden_user", "date": 1, "sender_user_name": "Anon"},
        }
    )
    assert filters.reply(replied) and not filters.reply(plain)
    assert filters.forwarded(forwarded) and not filters.forwarded(plain)
