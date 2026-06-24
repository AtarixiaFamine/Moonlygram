"""Tests for inline mode."""
from __future__ import annotations

from moonlygram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InlineQueryResultCachedSticker,
    InputTextMessageContent,
    SentWebAppMessage,
)
from moonlygram.ext import (
    Application,
    ChosenInlineResultHandler,
    InlineQueryHandler,
)
from moonlygram.types import Update
from conftest import (
    _msg,
    _update,
    fake_bot,
)


_INLINE_QUERY_RAW = {
    "update_id": 1,
    "inline_query": {
        "id": "q1",
        "from": {"id": 5, "is_bot": False, "first_name": "A"},
        "query": "cats",
        "offset": "",
    },
}

_CHOSEN_RESULT_RAW = {
    "update_id": 2,
    "chosen_inline_result": {
        "result_id": "r1",
        "from": {"id": 5, "is_bot": False, "first_name": "A"},
        "query": "cats",
    },
}


def test_inline_query_result_article_to_dict():
    article = InlineQueryResultArticle(
        "1",
        "Title",
        InputTextMessageContent("Hello", parse_mode="HTML"),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Go", url="https://x")]]),
        description="desc",
    )
    assert article.to_dict() == {
        "type": "article",
        "id": "1",
        "title": "Title",
        "description": "desc",
        "reply_markup": {"inline_keyboard": [[{"text": "Go", "url": "https://x"}]]},
        "input_message_content": {"message_text": "Hello", "parse_mode": "HTML"},
    }


def test_inline_query_result_cached_sticker_to_dict():
    result = InlineQueryResultCachedSticker("2", "STICKER_FILE_ID")
    assert result.to_dict() == {
        "type": "sticker", "id": "2", "sticker_file_id": "STICKER_FILE_ID"
    }


async def test_answer_inline_query_serializes_results_and_dict_escape_hatch():
    bot, session = fake_bot(True)
    results = [
        InlineQueryResultCachedSticker("1", "FID"),
        {"type": "voice", "id": "2", "voice_url": "https://x", "title": "V"},
    ]
    assert await bot.answer_inline_query("qid", results, cache_time=10) is True
    method, params = session.calls[0]
    assert method == "answerInlineQuery"
    assert params["results"] == [
        {"type": "sticker", "id": "1", "sticker_file_id": "FID"},
        {"type": "voice", "id": "2", "voice_url": "https://x", "title": "V"},
    ]
    assert params["cache_time"] == 10


async def test_answer_web_app_query_returns_sent_message():
    bot, session = fake_bot({"inline_message_id": "im1"})
    sent = await bot.answer_web_app_query("waq", InlineQueryResultCachedSticker("1", "FID"))
    assert isinstance(sent, SentWebAppMessage) and sent.inline_message_id == "im1"
    _, params = session.calls[0]
    assert params["result"] == {"type": "sticker", "id": "1", "sticker_file_id": "FID"}


def test_update_parses_inline_query_and_chosen_result():
    iq = Update.from_dict(_INLINE_QUERY_RAW)
    assert iq.inline_query is not None and iq.inline_query.query == "cats"
    assert iq.effective_user_id == 5
    assert iq.effective_chat_id is None

    cr = Update.from_dict(_CHOSEN_RESULT_RAW)
    assert cr.chosen_inline_result is not None
    assert cr.chosen_inline_result.result_id == "r1"
    assert cr.effective_user_id == 5


async def test_inline_query_handler_pattern_and_answer_shortcut():
    bot, session = fake_bot(True)
    app = Application(bot)
    seen: list[str] = []

    async def on_query(update, context):
        seen.append(update.inline_query.query)
        await update.inline_query.answer([InlineQueryResultCachedSticker("1", "FID")])

    app.add_handler(InlineQueryHandler(on_query, pattern=r"^cat"))
    await app.process_update(Update.from_dict(_INLINE_QUERY_RAW))
    await app.process_update(  # "dogs" does not match ^cat: ignored
        Update.from_dict(
            {"update_id": 3, "inline_query": dict(_INLINE_QUERY_RAW["inline_query"], query="dogs")}
        )
    )

    assert seen == ["cats"]
    assert session.calls == [
        (
            "answerInlineQuery",
            {
                "inline_query_id": "q1",
                "results": [{"type": "sticker", "id": "1", "sticker_file_id": "FID"}],
            },
        )
    ]


async def test_chosen_inline_result_handler_dispatch():
    bot, _ = fake_bot()
    app = Application(bot)
    seen: list[str] = []

    async def on_chosen(update, context):
        seen.append(update.chosen_inline_result.result_id)

    app.add_handler(ChosenInlineResultHandler(on_chosen))
    await app.process_update(Update.from_dict(_CHOSEN_RESULT_RAW))
    await app.process_update(_update(_msg("hi")))  # not a chosen result: ignored

    assert seen == ["r1"]
