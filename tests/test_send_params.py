"""The send/edit parameters added for full Bot API coverage.

test_method_coverage.py proves the parameters exist on the signatures; these
prove they reach the wire in the shape Telegram expects, including the object
and list-of-object values that have to be serialized on the way out.
"""
from __future__ import annotations

import json

import httpx
import pytest

from moonlygram import (
    Defaults,
    ForceReply,
    InputMediaPhoto,
    InputPollOption,
    LinkPreviewOptions,
    MessageEntity,
    ReplyKeyboardRemove,
    SuggestedPostParameters,
    SuggestedPostPrice,
)
from moonlygram.types import InputFile

from conftest import fake_bot, mock_bot

MESSAGE = {"message_id": 1, "date": 0, "chat": {"id": 5, "type": "private"}}


@pytest.mark.asyncio
async def test_send_message_forwards_thread_and_preview_options() -> None:
    bot, session = fake_bot(MESSAGE)

    await bot.send_message(
        5,
        "hi",
        message_thread_id=77,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        disable_notification=True,
        protect_content=True,
    )

    method, params = session.calls[0]
    assert method == "sendMessage"
    assert params["message_thread_id"] == 77
    assert params["link_preview_options"] == {"is_disabled": True}
    assert params["disable_notification"] is True
    assert params["protect_content"] is True


@pytest.mark.asyncio
async def test_entities_serialize_as_a_list_of_dicts() -> None:
    bot, session = fake_bot(MESSAGE)

    await bot.send_message(
        5,
        "bold text",
        entities=[MessageEntity.from_dict({"type": "bold", "offset": 0, "length": 4})],
    )

    _, params = session.calls[0]
    assert params["entities"] == [{"type": "bold", "offset": 0, "length": 4}]


@pytest.mark.asyncio
async def test_poll_options_accept_strings_and_objects() -> None:
    bot, session = fake_bot(MESSAGE)

    await bot.send_poll(
        5,
        "pick",
        ["plain", InputPollOption("fancy", text_parse_mode="HTML")],
        correct_option_ids=[1],
        open_period=60,
        type="quiz",
    )

    _, params = session.calls[0]
    # plain strings are normalized to the InputPollOption wire shape
    assert params["options"] == [
        {"text": "plain"},
        {"text": "fancy", "text_parse_mode": "HTML"},
    ]
    assert params["correct_option_ids"] == [1]
    assert params["open_period"] == 60


@pytest.mark.asyncio
async def test_poll_media_is_an_input_media_item() -> None:
    bot, session = fake_bot(MESSAGE)

    await bot.send_poll(
        5,
        "what is this",
        ["a", "b"],
        explanation="that",
        explanation_media=InputMediaPhoto("file-id"),
    )

    _, params = session.calls[0]
    assert params["explanation_media"] == {"type": "photo", "media": "file-id"}


@pytest.mark.asyncio
async def test_suggested_post_parameters_serialize() -> None:
    bot, session = fake_bot(MESSAGE)

    await bot.send_photo(
        5,
        "file-id",
        suggested_post_parameters=SuggestedPostParameters(
            price=SuggestedPostPrice("XTR", 500), send_date=99
        ),
    )

    _, params = session.calls[0]
    assert params["suggested_post_parameters"] == {
        "price": {"currency": "XTR", "amount": 500},
        "send_date": 99,
    }


@pytest.mark.asyncio
async def test_reply_keyboard_remove_and_force_reply_are_valid_markup() -> None:
    bot, session = fake_bot(MESSAGE)

    await bot.send_message(5, "gone", reply_markup=ReplyKeyboardRemove(selective=True))
    await bot.send_message(5, "answer", reply_markup=ForceReply())

    assert session.calls[0][1]["reply_markup"] == {
        "remove_keyboard": True,
        "selective": True,
    }
    assert session.calls[1][1]["reply_markup"] == {"force_reply": True}


@pytest.mark.asyncio
async def test_promote_chat_member_sends_channel_rights() -> None:
    bot, session = fake_bot(True)

    await bot.promote_chat_member(
        5, 9, can_post_messages=True, can_edit_messages=True, is_anonymous=False
    )

    _, params = session.calls[0]
    assert params["can_post_messages"] is True
    assert params["can_edit_messages"] is True
    # is_anonymous=False must survive: only None is dropped.
    assert params["is_anonymous"] is False


@pytest.mark.asyncio
async def test_defaults_now_reach_the_methods_that_expose_them() -> None:
    bot, session = fake_bot(MESSAGE)
    bot.defaults = Defaults(disable_notification=True, protect_content=True)

    await bot.send_message(5, "quiet")

    _, params = session.calls[0]
    assert params["disable_notification"] is True
    assert params["protect_content"] is True


@pytest.mark.asyncio
async def test_entities_survive_a_multipart_upload() -> None:
    """An InputFile forces multipart, where non-file values go through _to_form."""
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        body = request.content.decode("utf-8", "replace")
        seen["body"] = body
        return httpx.Response(200, json={"ok": True, "result": MESSAGE})

    bot = mock_bot(handler)
    await bot.send_photo(
        5,
        InputFile(b"bytes", "p.jpg"),
        caption="bold",
        caption_entities=[
            MessageEntity.from_dict({"type": "bold", "offset": 0, "length": 4})
        ],
        message_thread_id=12,
    )

    body = seen["body"]
    assert "12" in body
    # The entity list must be JSON, not a repr of the dataclass.
    assert json.dumps([{"type": "bold", "offset": 0, "length": 4}]) in body
    assert "MessageEntity(" not in body


@pytest.mark.asyncio
async def test_edit_rich_message_text_sends_rich_message() -> None:
    bot, session = fake_bot(MESSAGE)

    await bot.edit_rich_message_text(chat_id=5, message_id=1, markdown="**hi**")

    method, params = session.calls[0]
    assert method == "editMessageText"
    assert params["rich_message"] == {"markdown": "**hi**"}
