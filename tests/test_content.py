"""Tests for content sends (location/poll/media group/reactions)."""
from __future__ import annotations

from moonlygram import (
    InputMediaPhoto,
    InputMediaVideo,
    Message,
    Poll,
    ReactionTypeEmoji,
)
from moonlygram.ext import (
    filters,
)
from conftest import (
    _MESSAGE_DICT,
    _POLL_RAW,
    _msg,
    fake_bot,
)


class TestContentSends:
    async def test_send_location_and_poll_params(self):
        bot, session = fake_bot(_MESSAGE_DICT)
        await bot.send_location(1, 51.5, -0.12)
        assert session.calls[-1] == ("sendLocation", {"chat_id": 1, "latitude": 51.5, "longitude": -0.12})

        await bot.send_poll(1, "Pick", ["a", "b"], is_anonymous=False)
        method, params = session.calls[-1]
        assert method == "sendPoll"
        assert params == {"chat_id": 1, "question": "Pick", "options": ["a", "b"], "is_anonymous": False}

    async def test_send_sticker_with_file_id(self):
        bot, session = fake_bot(_MESSAGE_DICT)
        await bot.send_sticker(1, "CAACAg-file-id")
        assert session.calls == [("sendSticker", {"chat_id": 1, "sticker": "CAACAg-file-id"})]

    async def test_stop_poll_returns_poll(self):
        bot, _ = fake_bot(dict(_POLL_RAW, is_closed=True, options=[{"text": "a", "voter_count": 3}], total_voter_count=3))
        poll = await bot.stop_poll(1, 10)
        assert isinstance(poll, Poll)
        assert poll.is_closed and poll.options[0].voter_count == 3

    def test_message_parses_content_types(self):
        msg = Message.from_dict(
            {
                "message_id": 1,
                "chat": {"id": 1, "type": "private"},
                "poll": _POLL_RAW,
                "location": {"longitude": 1.0, "latitude": 2.0},
                "dice": {"emoji": "\N{GAME DIE}", "value": 4},
            }
        )
        assert msg.poll is not None and msg.poll.question == "Q?"
        assert msg.location is not None and msg.location.latitude == 2.0
        assert msg.dice is not None and msg.dice.value == 4

    def test_content_filters(self):
        poll_msg = Message.from_dict({"message_id": 1, "chat": {"id": 1, "type": "private"}, "poll": _POLL_RAW})
        loc_msg = Message.from_dict({"message_id": 1, "chat": {"id": 1, "type": "private"}, "location": {"longitude": 0.0, "latitude": 0.0}})
        assert filters.poll(poll_msg)
        assert not filters.poll(_msg("hi"))
        assert filters.location(loc_msg)
        assert not filters.location(poll_msg)


class TestMessagingAndEditing:
    async def test_send_media_group_serializes_and_parses(self):
        bot, session = fake_bot([_MESSAGE_DICT, _MESSAGE_DICT])
        msgs = await bot.send_media_group(1, [InputMediaPhoto("id1"), InputMediaVideo("id2", caption="c")])
        assert len(msgs) == 2 and all(isinstance(m, Message) for m in msgs)
        method, params = session.calls[0]
        assert method == "sendMediaGroup"
        assert params["media"] == [
            {"type": "photo", "media": "id1"},
            {"type": "video", "media": "id2", "caption": "c"},
        ]

    async def test_send_venue_params(self):
        bot, session = fake_bot(_MESSAGE_DICT)
        await bot.send_venue(1, 51.5, -0.1, "Big Ben", "London")
        assert session.calls == [
            ("sendVenue", {"chat_id": 1, "latitude": 51.5, "longitude": -0.1, "title": "Big Ben", "address": "London"})
        ]

    async def test_forward_and_delete_messages(self):
        bot, session = fake_bot([{"message_id": 11}, {"message_id": 12}])
        ids = await bot.forward_messages(2, 1, [11, 12])
        assert [m.message_id for m in ids] == [11, 12]
        assert session.calls[0] == ("forwardMessages", {"chat_id": 2, "from_chat_id": 1, "message_ids": [11, 12]})

        bot2, session2 = fake_bot(True)
        assert await bot2.delete_messages(1, [3, 4]) is True
        assert session2.calls == [("deleteMessages", {"chat_id": 1, "message_ids": [3, 4]})]

    async def test_set_message_reaction_serializes(self):
        bot, session = fake_bot(True)
        await bot.set_message_reaction(1, 5, reaction=[ReactionTypeEmoji("\N{THUMBS UP SIGN}")])
        _, params = session.calls[0]
        assert params["reaction"] == [{"type": "emoji", "emoji": "\N{THUMBS UP SIGN}"}]

    async def test_edit_message_live_location_parses(self):
        bot, _ = fake_bot(_MESSAGE_DICT)
        result = await bot.edit_message_live_location(1.0, 2.0, chat_id=1, message_id=9)
        assert isinstance(result, Message)

    def test_message_parses_venue_and_filter(self):
        msg = Message.from_dict(
            {
                "message_id": 1,
                "chat": {"id": 1, "type": "private"},
                "venue": {"location": {"longitude": 1.0, "latitude": 2.0}, "title": "T", "address": "A"},
            }
        )
        assert msg.venue is not None and msg.venue.title == "T" and msg.venue.location.latitude == 2.0
        assert filters.venue(msg)
        assert not filters.venue(_msg("hi"))
