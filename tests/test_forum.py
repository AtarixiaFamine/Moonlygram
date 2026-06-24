"""Tests for forum topics."""
from __future__ import annotations

from moonlygram import (
    ForumTopic,
)
from conftest import (
    fake_bot,
)


async def test_create_forum_topic_parses():
    bot, session = fake_bot(
        {"message_thread_id": 42, "name": "Support", "icon_color": 7322096}
    )
    topic = await bot.create_forum_topic(1, "Support", icon_color=7322096)
    assert isinstance(topic, ForumTopic)
    assert topic.message_thread_id == 42 and topic.name == "Support"
    assert session.calls == [
        ("createForumTopic", {"chat_id": 1, "name": "Support", "icon_color": 7322096})
    ]


async def test_forum_topic_bool_methods():
    bot, session = fake_bot(True)
    assert await bot.close_forum_topic(1, 42) is True
    assert session.calls[0] == ("closeForumTopic", {"chat_id": 1, "message_thread_id": 42})

    assert await bot.edit_general_forum_topic(1, "General") is True
    assert session.calls[1] == ("editGeneralForumTopic", {"chat_id": 1, "name": "General"})

    assert await bot.hide_general_forum_topic(1) is True
    assert session.calls[2] == ("hideGeneralForumTopic", {"chat_id": 1})


async def test_get_forum_topic_icon_stickers_parses():
    bot, _ = fake_bot(
        [
            {
                "file_id": "s1",
                "file_unique_id": "u1",
                "type": "custom_emoji",
                "width": 100,
                "height": 100,
            }
        ]
    )
    stickers = await bot.get_forum_topic_icon_stickers()
    assert len(stickers) == 1 and stickers[0].file_id == "s1"
