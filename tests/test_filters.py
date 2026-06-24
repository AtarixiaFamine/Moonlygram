"""Tests for message filters."""
from __future__ import annotations

from moonlygram import (
    Message,
)
from moonlygram.ext import (
    filters,
)
from conftest import (
    _FULL_MESSAGE_RAW,
    _msg,
)


class TestFilters:
    def test_command_filter_matches_plain_and_addressed(self):
        assert filters.command("start")(_msg("/start"))
        assert filters.command("start")(_msg("/start@MyBot now"))
        assert not filters.command("start")(_msg("/stop"))
        assert not filters.command("start")(_msg("hello"))

    def test_command_filter_matches_any_of_several_names(self):
        f = filters.command("start", "help")
        assert f(_msg("/start"))
        assert f(_msg("/help"))
        assert not f(_msg("/stop"))

    def test_private_filter(self):
        assert filters.private(_msg("hi"))
        assert not filters.private(_msg("hi", chat_type="group"))

    def test_filter_combinators(self):
        f = filters.command("ban") & filters.group
        assert f(_msg("/ban", chat_type="group"))
        assert not f(_msg("/ban", chat_type="private"))

        either = filters.command("a") | filters.command("b")
        assert either(_msg("/a")) and either(_msg("/b"))
        assert not either(_msg("/c"))

        assert (~filters.private)(_msg("hi", chat_type="group"))
        assert not (~filters.private)(_msg("hi"))

    def test_regex_filter(self):
        f = filters.regex(r"\bhello\b")
        assert f(_msg("well hello there"))
        assert not f(_msg("goodbye"))


class TestNewFilters:
    def test_via_bot_filter(self):
        assert filters.via_bot(Message.from_dict(_FULL_MESSAGE_RAW))
        assert not filters.via_bot(_msg("hi", from_id=5))

    def test_username_and_chat_username_filters(self):
        msg = Message.from_dict(
            {
                "message_id": 1,
                "chat": {"id": 1, "type": "supergroup", "username": "mychat"},
                "from": {"id": 5, "is_bot": False, "first_name": "A", "username": "alice"},
                "text": "hi",
            }
        )
        assert filters.username("alice")(msg)
        assert filters.username("@alice")(msg)
        assert not filters.username("bob")(msg)
        assert filters.chat_username("@mychat")(msg)
        assert not filters.chat_username("other")(msg)
        assert not filters.username("alice")(_msg("hi"))

    def test_forwarded_from_filter(self):
        from_user = Message.from_dict(
            {
                "message_id": 1,
                "chat": {"id": 1, "type": "private"},
                "forward_origin": {
                    "type": "user",
                    "date": 1,
                    "sender_user": {"id": 77, "is_bot": False, "first_name": "Orig"},
                },
            }
        )
        from_channel = Message.from_dict(
            {
                "message_id": 2,
                "chat": {"id": 1, "type": "private"},
                "forward_origin": {
                    "type": "channel",
                    "date": 1,
                    "chat": {"id": -100, "type": "channel"},
                    "message_id": 5,
                },
            }
        )
        assert filters.forwarded_from(77)(from_user)
        assert filters.forwarded_from(-100)(from_channel)
        assert not filters.forwarded_from(1)(from_user)
        assert not filters.forwarded_from(77)(_msg("hi"))

    def test_entity_filter(self):
        msg = Message.from_dict(
            {
                "message_id": 1,
                "chat": {"id": 1, "type": "private"},
                "text": "see https://x.io #tag",
                "entities": [
                    {"type": "url", "offset": 4, "length": 12},
                    {"type": "hashtag", "offset": 17, "length": 4},
                ],
            }
        )
        assert filters.entity("url")(msg)
        assert filters.entity("mention", "hashtag")(msg)
        assert not filters.entity("mention")(msg)
        assert not filters.entity("url")(_msg("no entities"))

    def test_mime_type_filter(self):
        msg = Message.from_dict(
            {
                "message_id": 1,
                "chat": {"id": 1, "type": "private"},
                "document": {
                    "file_id": "f",
                    "file_unique_id": "u",
                    "mime_type": "application/pdf",
                },
            }
        )
        assert filters.mime_type("application/pdf")(msg)
        assert filters.mime_type("image/png", "application/pdf")(msg)
        assert not filters.mime_type("image/png")(msg)
        assert not filters.mime_type("application/pdf")(_msg("hi"))
