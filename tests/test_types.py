"""Tests for received-type parsing completeness."""
from __future__ import annotations

from moonlygram import (
    InlineKeyboardButton,
    KeyboardButton,
    Message,
    MessageOrigin,
    MessageReactionUpdated,
    ReactionTypeCustomEmoji,
    ReactionTypeEmoji,
    ReactionTypePaid,
    User,
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


def test_user_parses_language_code():
    user = User.from_dict({"id": 1, "first_name": "A", "language_code": "en"})
    assert user.language_code == "en"
    assert User.from_dict({"id": 1, "first_name": "A"}).language_code is None


def test_inline_keyboard_button_serializes_style_and_icon():
    button = InlineKeyboardButton(
        "Buy", callback_data="pay", style="primary", icon_custom_emoji_id="55"
    )
    assert button.to_dict() == {
        "text": "Buy",
        "callback_data": "pay",
        "style": "primary",
        "icon_custom_emoji_id": "55",
    }


def test_keyboard_button_serializes_style_and_icon():
    assert KeyboardButton("Go", style="danger", icon_custom_emoji_id="7").to_dict() == {
        "text": "Go",
        "style": "danger",
        "icon_custom_emoji_id": "7",
    }


def test_buttons_omit_style_and_icon_when_unset():
    assert InlineKeyboardButton("Plain", url="https://x").to_dict() == {
        "text": "Plain",
        "url": "https://x",
    }
    assert KeyboardButton("Plain").to_dict() == {"text": "Plain"}


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


def test_disabled_button_serializes_as_an_empty_object():
    from moonlygram import DisabledButton

    button = InlineKeyboardButton("Soon", callback_data="x", disabled=DisabledButton())
    assert button.to_dict() == {
        "text": "Soon",
        "callback_data": "x",
        "disabled": {},
    }
    # Unset, the field stays out of the payload entirely.
    assert "disabled" not in InlineKeyboardButton("Go", callback_data="x").to_dict()


def test_copy_text_button_round_trips():
    from moonlygram import CopyTextButton

    button = InlineKeyboardButton("Copy code", copy_text=CopyTextButton("ABC-123"))
    assert button.to_dict() == {
        "text": "Copy code",
        "copy_text": {"text": "ABC-123"},
    }
    assert InlineKeyboardButton.from_dict(button.to_dict()) == button


def test_inline_keyboard_button_serializes_the_rest_of_the_spec():
    button = InlineKeyboardButton(
        "Open",
        web_app={"url": "https://app"},
        login_url={"url": "https://login"},
        switch_inline_query="q",
        switch_inline_query_current_chat="here",
        switch_inline_query_chosen_chat={"query": "q", "allow_user_chats": True},
        callback_game={},
        pay=True,
    )
    assert button.to_dict() == {
        "text": "Open",
        "web_app": {"url": "https://app"},
        "login_url": {"url": "https://login"},
        "switch_inline_query": "q",
        "switch_inline_query_current_chat": "here",
        "switch_inline_query_chosen_chat": {"query": "q", "allow_user_chats": True},
        "callback_game": {},
        "pay": True,
    }


def test_keyboard_button_serializes_its_request_fields():
    assert KeyboardButton("Share", request_contact=True).to_dict() == {
        "text": "Share",
        "request_contact": True,
    }
    assert KeyboardButton("Pick", request_users={"request_id": 1}).to_dict() == {
        "text": "Pick",
        "request_users": {"request_id": 1},
    }


def test_reply_keyboard_markup_serializes_its_remaining_fields():
    from moonlygram import ReplyKeyboardMarkup

    assert ReplyKeyboardMarkup(
        [[KeyboardButton("a")]],
        is_persistent=True,
        input_field_placeholder="Type here",
        selective=True,
    ).to_dict() == {
        "keyboard": [[{"text": "a"}]],
        "is_persistent": True,
        "input_field_placeholder": "Type here",
        "selective": True,
    }


def test_message_parses_its_reply_markup():
    from moonlygram import CopyTextButton, InlineKeyboardMarkup

    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Copy", copy_text=CopyTextButton("ABC-123")),
                InlineKeyboardButton("Go", url="https://x", style="primary"),
            ]
        ],
        force_reply=True,
    )
    msg = Message.from_dict(
        {
            "message_id": 1,
            "chat": {"id": -100, "type": "channel"},
            "text": "hi",
            "reply_markup": markup.to_dict(),
        }
    )
    # An edit that re-sends the parsed markup must put back what came in;
    # Telegram drops the whole keyboard from any edit that omits it.
    assert msg.reply_markup == markup
    assert msg.reply_markup.to_dict() == markup.to_dict()
    assert Message.from_dict(
        {"message_id": 2, "chat": {"id": 1, "type": "private"}}
    ).reply_markup is None


def test_both_markups_can_force_a_reply():
    from moonlygram import InlineKeyboardMarkup, ReplyKeyboardMarkup

    inline = InlineKeyboardMarkup(
        [[InlineKeyboardButton("a", callback_data="b")]], force_reply=True
    )
    reply = ReplyKeyboardMarkup([[KeyboardButton("a")]], force_reply=True)
    assert inline.to_dict()["force_reply"] is True
    assert reply.to_dict()["force_reply"] is True
    assert "force_reply" not in ReplyKeyboardMarkup([[KeyboardButton("a")]]).to_dict()


def test_unique_gift_info_parses_its_10_3_fields():
    from moonlygram import Message

    msg = Message.from_dict(
        {
            "message_id": 1,
            "chat": {"id": 1, "type": "private"},
            "unique_gift": {
                "origin": "upgrade",
                "text": "for you",
                "is_private": True,
                "entities": [{"type": "bold", "offset": 0, "length": 3}],
                "gift": {"gift_id": "g1", "name": "n", "number": 7},
            },
        }
    )
    gift = msg.unique_gift
    assert gift is not None
    assert (gift.text, gift.is_private, gift.origin) == ("for you", True, "upgrade")
    assert gift.entities is not None and gift.entities[0].type == "bold"
    assert gift.gift.number == 7
