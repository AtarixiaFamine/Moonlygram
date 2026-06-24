"""Tests for Update parsing and the update-type handlers."""
from __future__ import annotations

from moonlygram import (
    Message,
    ReactionTypeEmoji,
)
from moonlygram.ext import (
    Application,
    ChatBoostHandler,
    CommandHandler,
    MessageHandler,
    MessageReactionHandler,
    PollAnswerHandler,
    PollHandler,
    filters,
)
from moonlygram.types import Update
from conftest import (
    _MESSAGE_DICT,
    _POLL_RAW,
    _msg,
    _update,
    fake_bot,
)


_POLL_ANSWER_RAW = {
    "update_id": 1,
    "poll_answer": {
        "poll_id": "p1",
        "user": {"id": 5, "is_bot": False, "first_name": "A"},
        "option_ids": [0, 2],
    },
}

_MESSAGE_REACTION_RAW = {
    "update_id": 2,
    "message_reaction": {
        "chat": {"id": 100, "type": "supergroup"},
        "message_id": 7,
        "user": {"id": 5, "is_bot": False, "first_name": "A"},
        "date": 0,
        "old_reaction": [],
        "new_reaction": [{"type": "emoji", "emoji": "\N{THUMBS UP SIGN}"}],
    },
}

_MESSAGE_REACTION_COUNT_RAW = {
    "update_id": 3,
    "message_reaction_count": {
        "chat": {"id": 100, "type": "channel"},
        "message_id": 7,
        "date": 0,
        "reactions": [
            {"type": {"type": "emoji", "emoji": "\N{THUMBS UP SIGN}"}, "total_count": 4}
        ],
    },
}

_CHAT_BOOST_RAW = {
    "update_id": 4,
    "chat_boost": {
        "chat": {"id": 100, "type": "channel"},
        "boost": {
            "boost_id": "b1",
            "add_date": 100,
            "expiration_date": 200,
            "source": {
                "source": "premium",
                "user": {"id": 9, "is_bot": False, "first_name": "U"},
            },
        },
    },
}

_REMOVED_CHAT_BOOST_RAW = {
    "update_id": 5,
    "removed_chat_boost": {
        "chat": {"id": 100, "type": "channel"},
        "boost_id": "b1",
        "remove_date": 300,
        "source": {
            "source": "premium",
            "user": {"id": 9, "is_bot": False, "first_name": "U"},
        },
    },
}


class TestUpdateCompletion:
    def test_update_parses_edited_and_channel_posts(self):
        edited = Update.from_dict({"update_id": 1, "edited_message": dict(_MESSAGE_DICT, text="fixed")})
        assert edited.edited_message is not None
        assert edited.effective_message is not None and edited.effective_message.text == "fixed"

        channel = Update.from_dict({"update_id": 2, "channel_post": dict(_MESSAGE_DICT, text="news")})
        assert channel.channel_post is not None
        assert channel.effective_message is not None and channel.effective_message.text == "news"

    async def test_message_handler_matches_edited_message(self):
        bot, _ = fake_bot()
        app = Application(bot)
        hits: list[str | None] = []

        async def echo(update, context):
            hits.append(update.effective_message.text)

        app.add_handler(MessageHandler(filters.text, echo))
        await app.process_update(
            Update.from_dict({"update_id": 1, "edited_message": dict(_MESSAGE_DICT, text="edited!")})
        )
        assert hits == ["edited!"]

    async def test_command_handler_matches_channel_post(self):
        bot, _ = fake_bot()
        app = Application(bot)
        seen: list[list[str] | None] = []

        async def go(update, context):
            seen.append(context.args)

        app.add_handler(CommandHandler("go", go))
        await app.process_update(
            Update.from_dict({"update_id": 1, "channel_post": dict(_MESSAGE_DICT, text="/go a b")})
        )
        assert seen == [["a", "b"]]

    def test_message_parses_entities(self):
        msg = Message.from_dict(
            {
                "message_id": 1,
                "chat": {"id": 1, "type": "private"},
                "text": "hi @bob",
                "entities": [{"type": "mention", "offset": 3, "length": 4}],
            }
        )
        assert msg.entities is not None
        assert msg.entities[0].type == "mention" and msg.entities[0].offset == 3

    def test_channel_filter(self):
        channel_msg = Message.from_dict({"message_id": 1, "chat": {"id": 1, "type": "channel"}, "text": "x"})
        assert filters.channel(channel_msg)
        assert not filters.channel(_msg("x"))


class TestUpdateTypeHandlers:
    def test_update_parses_poll_and_poll_answer(self):
        poll = Update.from_dict({"update_id": 1, "poll": _POLL_RAW})
        assert poll.poll is not None and poll.poll.question == "Q?"
        assert poll.effective_chat_id is None and poll.effective_user_id is None

        answer = Update.from_dict(_POLL_ANSWER_RAW)
        assert answer.poll_answer is not None
        assert answer.poll_answer.poll_id == "p1"
        assert answer.poll_answer.option_ids == [0, 2]
        assert answer.effective_user_id == 5

    async def test_poll_and_poll_answer_handler_dispatch(self):
        bot, _ = fake_bot()
        app = Application(bot)
        seen: list[str] = []

        async def on_poll(update, context):
            seen.append(f"poll:{update.poll.id}")

        async def on_answer(update, context):
            seen.append(f"answer:{update.poll_answer.poll_id}")

        app.add_handler(PollHandler(on_poll))
        app.add_handler(PollAnswerHandler(on_answer))
        await app.process_update(Update.from_dict({"update_id": 1, "poll": _POLL_RAW}))
        await app.process_update(Update.from_dict(_POLL_ANSWER_RAW))
        await app.process_update(_update(_msg("hi")))  # neither: ignored

        assert seen == ["poll:p", "answer:p1"]

    def test_update_parses_message_reaction(self):
        update = Update.from_dict(_MESSAGE_REACTION_RAW)
        assert update.message_reaction is not None
        reaction = update.message_reaction.new_reaction[0]
        assert isinstance(reaction, ReactionTypeEmoji)
        assert reaction.emoji == "\N{THUMBS UP SIGN}"
        assert update.effective_chat_id == 100
        assert update.effective_user_id == 5

        count = Update.from_dict(_MESSAGE_REACTION_COUNT_RAW)
        assert count.message_reaction_count is not None
        counted = count.message_reaction_count.reactions[0]
        assert counted.total_count == 4
        assert isinstance(counted.type, ReactionTypeEmoji)
        assert counted.type.emoji == "\N{THUMBS UP SIGN}"
        assert count.effective_chat_id == 100
        assert count.effective_user_id is None

    async def test_message_reaction_handler_kind_narrows(self):
        bot, _ = fake_bot()
        app = Application(bot)
        seen: list[str] = []

        async def on_reaction(update, context):
            seen.append("reaction")

        app.add_handler(
            MessageReactionHandler(
                on_reaction, kind=MessageReactionHandler.MESSAGE_REACTION
            )
        )
        await app.process_update(Update.from_dict(_MESSAGE_REACTION_RAW))
        await app.process_update(  # the count variant: ignored by this kind
            Update.from_dict(_MESSAGE_REACTION_COUNT_RAW)
        )

        assert seen == ["reaction"]

    def test_update_parses_chat_boost(self):
        boost = Update.from_dict(_CHAT_BOOST_RAW)
        assert boost.chat_boost is not None
        assert boost.chat_boost.boost.boost_id == "b1"
        assert boost.effective_chat_id == 100
        assert boost.effective_user_id == 9

        removed = Update.from_dict(_REMOVED_CHAT_BOOST_RAW)
        assert removed.removed_chat_boost is not None
        assert removed.removed_chat_boost.boost_id == "b1"
        assert removed.removed_chat_boost.source.source == "premium"
        assert removed.effective_chat_id == 100
        assert removed.effective_user_id == 9

    async def test_chat_boost_handler_dispatch(self):
        bot, _ = fake_bot()
        app = Application(bot)
        seen: list[str] = []

        async def on_boost(update, context):
            seen.append("added" if update.chat_boost is not None else "removed")

        app.add_handler(ChatBoostHandler(on_boost))
        await app.process_update(Update.from_dict(_CHAT_BOOST_RAW))
        await app.process_update(Update.from_dict(_REMOVED_CHAT_BOOST_RAW))
        await app.process_update(_update(_msg("hi")))  # not a boost: ignored

        assert seen == ["added", "removed"]
