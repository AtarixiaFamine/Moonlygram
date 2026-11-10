"""Tests for widgets, TON wallet objects, and chat share themes (Bot API 10.4).

A widget is HTML inside a message, so almost everything here is about what
reaches the wire and what comes back off it. The query half gets the most
attention: a widget that raises a query has three shapes of query type, and the
answer has to find its way back to a message the query may not name directly.
"""
from __future__ import annotations

from typing import Any

from moonlygram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputSharedWidgetMessageContent,
    InputWidgetMessageContent,
    MessageEntity,
    Message,
    ReplyParameters,
    SharedWidgetQuery,
    Update,
    WidgetQuery,
)
from moonlygram.ext import SharedWidgetQueryHandler, WidgetQueryHandler
from conftest import _MESSAGE_DICT, fake_bot

_WIDGET_HTML = "<div>hi</div>"

# A widget query from a message. The "data" variant carries the user's wallet
# card; the signing and transaction variants carry the wallet itself.
_QUERY_RAW: dict[str, Any] = {
    "id": "q1",
    "from": {"id": 5, "is_bot": False, "first_name": "A"},
    "chat": {"id": 100, "type": "private"},
    "message_id": 42,
    "chat_instance": "ci",
    "type": {
        "type": "data",
        "wallet_card": {
            "address": "EQC_addr",
            "amount": "1500000000",
            "stickers": [
                {
                    "position": {
                        "x_percentage": 50.0,
                        "y_percentage": 25.0,
                        "width_percentage": 10.0,
                        "height_percentage": 10.0,
                        "rotation_angle": 0.0,
                        "corner_radius_percentage": 5.0,
                    },
                    "nft": {
                        "address": "EQC_nft",
                        "index": "7",
                        "name": "Plush Pepe",
                        "description": "A rare one",
                        "attributes": [{"trait_type": "Model", "value": "Pepe"}],
                    },
                }
            ],
            "background_nft_address": "EQC_nft",
        },
    },
    "data": "clicked",
    "widget_id": "w1",
}

_SHARED_QUERY_RAW: dict[str, Any] = {
    "id": "q2",
    "from": {"id": 6, "is_bot": False, "first_name": "B"},
    "type": {
        "type": "sent_transaction",
        "wallet": {
            "address": "EQC_addr",
            "amount": "90",
            "public_key": "aabb",
            "state_init": "c3RhdGU=",
        },
        "msg_hash": "deadbeef",
    },
    "data": "tx",
    "widget_id": "w1",
}


class TestSendingWidgets:
    async def test_send_widget_builds_the_whole_payload(self):
        bot, session = fake_bot(_MESSAGE_DICT)
        await bot.send_widget(
            1,
            _WIDGET_HTML,
            width=300,
            height=120,
            public_data="shared-state",
            chat_data="per-message",
            caption="A widget",
            caption_entities=[MessageEntity(type="bold", offset=0, length=1)],
            show_caption_above_media=True,
            allow_queries=True,
            is_shared=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("go", callback_data="g")]]
            ),
            reply_parameters=ReplyParameters(message_id=9),
        )
        method, params = session.calls[0]
        assert method == "sendWidget"
        assert params["chat_id"] == 1
        assert params["html"] == _WIDGET_HTML
        assert params["width"] == 300 and params["height"] == 120
        assert params["public_data"] == "shared-state"
        assert params["chat_data"] == "per-message"
        assert params["allow_queries"] is True and params["is_shared"] is True
        assert params["show_caption_above_media"] is True
        assert params["caption_entities"] == [
            {"type": "bold", "offset": 0, "length": 1}
        ]
        assert params["reply_parameters"] == {"message_id": 9}
        assert "inline_keyboard" in params["reply_markup"]

    async def test_send_widget_omits_what_was_not_set(self):
        bot, session = fake_bot(_MESSAGE_DICT)
        await bot.send_widget(1, _WIDGET_HTML)
        _, params = session.calls[0]
        assert params == {"chat_id": 1, "html": _WIDGET_HTML}

    async def test_send_shared_widget_sends_the_id_not_the_html(self):
        bot, session = fake_bot(_MESSAGE_DICT)
        await bot.send_shared_widget(1, "w1", chat_data="again", caption="Reused")
        method, params = session.calls[0]
        assert method == "sendSharedWidget"
        assert params == {
            "chat_id": 1,
            "widget_id": "w1",
            "chat_data": "again",
            "caption": "Reused",
        }
        assert "html" not in params


class TestAnsweringAndEditing:
    async def test_answer_widget_query(self):
        bot, session = fake_bot(True)
        assert await bot.answer_widget_query("q1", data="pong") is True
        assert session.calls[0] == ("answerWidgetQuery", {
            "widget_query_id": "q1",
            "data": "pong",
        })

    async def test_answer_widget_query_without_data(self):
        bot, session = fake_bot(True)
        await bot.answer_widget_query("q1")
        assert session.calls[0][1] == {"widget_query_id": "q1"}

    async def test_edit_message_widget_data_by_message(self):
        bot, session = fake_bot(True)
        await bot.edit_message_widget_data(
            chat_id=100, message_id=42, public_data="v2", chat_data="local"
        )
        method, params = session.calls[0]
        assert method == "editMessageWidgetData"
        assert params == {
            "chat_id": 100,
            "message_id": 42,
            "public_data": "v2",
            "chat_data": "local",
        }

    async def test_edit_message_widget_data_by_inline_message(self):
        bot, session = fake_bot(True)
        await bot.edit_message_widget_data(inline_message_id="im1", public_data="v2")
        _, params = session.calls[0]
        assert params == {"inline_message_id": "im1", "public_data": "v2"}

    async def test_empty_public_data_is_sent_rather_than_dropped(self):
        """An empty string clears the data, so it must survive None-dropping."""
        bot, session = fake_bot(True)
        await bot.edit_message_widget_data(chat_id=1, message_id=2, public_data="")
        _, params = session.calls[0]
        assert params["public_data"] == ""

    async def test_edit_shared_widget_data(self):
        bot, session = fake_bot(True)
        assert await bot.edit_shared_widget_data("w1", "v3", cache_time=60) is True
        assert session.calls[0] == ("editSharedWidgetData", {
            "widget_id": "w1",
            "public_data": "v3",
            "cache_time": 60,
        })


class TestReceivingWidgets:
    def test_message_parses_a_widget(self):
        message = Message.from_dict({
            **_MESSAGE_DICT,
            "widget": {
                "id": "w1",
                "html": _WIDGET_HTML,
                "width": 300,
                "public_data": "shared-state",
                "chat_data": "per-message",
            },
        })
        assert message.widget is not None
        assert message.widget.id == "w1"
        assert message.widget.html == _WIDGET_HTML
        assert message.widget.width == 300
        # height was not sent, so the widget sizes itself
        assert message.widget.height is None

    def test_message_parses_a_ton_wallet_transfer(self):
        message = Message.from_dict({
            **_MESSAGE_DICT,
            "ton_wallet_transfer": {
                "transaction_id": "t1",
                "peer_address": "EQC_peer",
                "amount": "-250",
                "comment": "thanks",
            },
        })
        transfer = message.ton_wallet_transfer
        assert transfer is not None
        # negative means outgoing, and the amount stays a string: it is in the
        # smallest units and does not fit a float without losing precision
        assert transfer.amount == "-250"
        assert transfer.peer_address == "EQC_peer"
        assert transfer.comment == "thanks"

    def test_message_parses_paid_messages_waived(self):
        """The service message carries no fields, so its presence is the signal."""
        message = Message.from_dict({**_MESSAGE_DICT, "paid_messages_waived": {}})
        assert message.paid_messages_waived is not None

    def test_widget_query_parses_its_wallet_card(self):
        update = Update.from_dict({"update_id": 1, "widget_query": _QUERY_RAW})
        query = update.widget_query
        assert query is not None
        assert query.id == "q1"
        assert query.data == "clicked"
        assert query.widget_id == "w1"
        assert query.chat is not None and query.chat.id == 100
        assert query.message_id == 42
        assert query.type.type == "data"
        card = query.type.wallet_card
        assert card is not None
        assert card.address == "EQC_addr"
        sticker = card.stickers[0]
        assert sticker.position.x_percentage == 50.0
        assert sticker.nft.name == "Plush Pepe"
        assert sticker.nft.attributes is not None
        assert sticker.nft.attributes[0].trait_type == "Model"

    def test_shared_widget_query_parses_a_sent_transaction(self):
        update = Update.from_dict(
            {"update_id": 1, "shared_widget_query": _SHARED_QUERY_RAW}
        )
        query = update.shared_widget_query
        assert query is not None
        assert query.widget_id == "w1"
        assert query.type.type == "sent_transaction"
        assert query.type.msg_hash == "deadbeef"
        assert query.type.wallet is not None
        assert query.type.wallet.public_key == "aabb"
        # a forwarded shared widget names no chat or message
        assert not hasattr(query, "chat")

    def test_sign_data_variant_keeps_its_own_field(self):
        raw = {
            **_SHARED_QUERY_RAW,
            "type": {
                "type": "sign_data",
                "wallet": {"address": "EQC_addr", "amount": "0"},
                "sign_data": "payload-to-sign",
            },
        }
        query = SharedWidgetQuery.from_dict(raw)
        assert query.type.sign_data == "payload-to-sign"
        assert query.type.msg_hash is None

    def test_widget_query_fills_the_effective_properties(self):
        update = Update.from_dict({"update_id": 1, "widget_query": _QUERY_RAW})
        assert update.effective_user_id == 5
        assert update.effective_chat_id == 100

    def test_shared_widget_query_has_a_user_but_no_chat(self):
        update = Update.from_dict(
            {"update_id": 1, "shared_widget_query": _SHARED_QUERY_RAW}
        )
        assert update.effective_user_id == 6
        assert update.effective_chat_id is None


class TestBoundShortcuts:
    async def test_answer_goes_through_the_bound_bot(self):
        bot, session = fake_bot(True)
        update = Update.from_dict({"update_id": 1, "widget_query": _QUERY_RAW})
        update.set_bot(bot)
        assert update.widget_query is not None
        await update.widget_query.answer("pong")
        assert session.calls[0] == ("answerWidgetQuery", {
            "widget_query_id": "q1",
            "data": "pong",
        })

    async def test_edit_widget_data_uses_the_querys_message(self):
        bot, session = fake_bot(True)
        update = Update.from_dict({"update_id": 1, "widget_query": _QUERY_RAW})
        update.set_bot(bot)
        assert update.widget_query is not None
        await update.widget_query.edit_widget_data(public_data="v2")
        _, params = session.calls[0]
        assert params == {"chat_id": 100, "message_id": 42, "public_data": "v2"}

    async def test_edit_widget_data_prefers_an_inline_message_id(self):
        bot, session = fake_bot(True)
        raw = {
            k: v for k, v in _QUERY_RAW.items() if k not in ("chat", "message_id")
        }
        raw["inline_message_id"] = "im1"
        query = WidgetQuery.from_dict(raw)
        query.set_bot(bot)
        await query.edit_widget_data(chat_data="local")
        _, params = session.calls[0]
        assert params == {"inline_message_id": "im1", "chat_data": "local"}

    async def test_shared_query_answers_too(self):
        bot, session = fake_bot(True)
        query = SharedWidgetQuery.from_dict(_SHARED_QUERY_RAW)
        query.set_bot(bot)
        await query.answer()
        assert session.calls[0] == ("answerWidgetQuery", {"widget_query_id": "q2"})

    def test_set_bot_reaches_the_sender(self):
        bot, _ = fake_bot()
        update = Update.from_dict({"update_id": 1, "widget_query": _QUERY_RAW})
        update.set_bot(bot)
        assert update.widget_query is not None
        assert update.widget_query.from_user._bot is bot
        assert update.widget_query.chat is not None
        assert update.widget_query.chat._bot is bot


class TestHandlers:
    def test_widget_query_handler_matches_only_its_update(self):
        async def cb(update, context):  # pragma: no cover - never run
            pass

        handler = WidgetQueryHandler(cb)
        assert handler.check_update(
            Update.from_dict({"update_id": 1, "widget_query": _QUERY_RAW})
        )
        assert not handler.check_update(
            Update.from_dict({"update_id": 1, "shared_widget_query": _SHARED_QUERY_RAW})
        )
        assert not handler.check_update(Update(update_id=1))

    def test_widget_query_handler_pattern_filters_on_data(self):
        async def cb(update, context):  # pragma: no cover - never run
            pass

        update = Update.from_dict({"update_id": 1, "widget_query": _QUERY_RAW})
        assert WidgetQueryHandler(cb, pattern="click").check_update(update)
        assert not WidgetQueryHandler(cb, pattern="^nope$").check_update(update)

    def test_shared_widget_query_handler(self):
        async def cb(update, context):  # pragma: no cover - never run
            pass

        update = Update.from_dict(
            {"update_id": 1, "shared_widget_query": _SHARED_QUERY_RAW}
        )
        assert SharedWidgetQueryHandler(cb).check_update(update)
        assert SharedWidgetQueryHandler(cb, pattern="tx").check_update(update)
        assert not SharedWidgetQueryHandler(cb, pattern="zzz").check_update(update)
        assert not SharedWidgetQueryHandler(cb).check_update(
            Update.from_dict({"update_id": 1, "widget_query": _QUERY_RAW})
        )

    async def test_application_dispatches_a_widget_query(self):
        from moonlygram.ext import Application

        bot, _ = fake_bot(True)
        app = Application(bot)
        seen: dict[str, Any] = {}

        async def on_query(update, context):
            seen["data"] = update.widget_query.data

        app.add_handler(WidgetQueryHandler(on_query))
        await app.process_update(
            Update.from_dict({"update_id": 1, "widget_query": _QUERY_RAW})
        )
        assert seen["data"] == "clicked"


class TestInlineContent:
    def test_widget_content_serializes_through_an_inline_result(self):
        result = InlineQueryResultArticle(
            id="r1",
            title="A widget",
            input_message_content=InputWidgetMessageContent(
                html=_WIDGET_HTML,
                width=200,
                public_data="p",
                caption="cap",
                caption_entities=[MessageEntity(type="bold", offset=0, length=3)],
                allow_queries=True,
                is_shared=True,
            ),
        )
        content = result.to_dict()["input_message_content"]
        assert content == {
            "html": _WIDGET_HTML,
            "width": 200,
            "public_data": "p",
            "caption": "cap",
            "allow_queries": True,
            "is_shared": True,
            "caption_entities": [{"type": "bold", "offset": 0, "length": 3}],
        }

    def test_shared_widget_content_carries_only_the_id(self):
        content = InputSharedWidgetMessageContent(widget_id="w1", caption="cap")
        assert content.to_dict() == {"widget_id": "w1", "caption": "cap"}


class TestShareThemes:
    async def test_get_chat_share_theme_backdrops_parses(self):
        bot, session = fake_bot({
            "backdrops": [
                {
                    "id": 3,
                    "name": "Midnight",
                    "colors": {
                        "center_color": 1,
                        "edge_color": 2,
                        "symbol_color": 3,
                        "text_color": 4,
                    },
                }
            ]
        })
        backdrops = await bot.get_chat_share_theme_backdrops()
        assert session.calls[0] == ("getChatShareThemeBackdrops", {})
        assert len(backdrops.backdrops) == 1
        backdrop = backdrops.backdrops[0]
        assert backdrop.id == 3 and backdrop.name == "Midnight"
        assert backdrop.colors.center_color == 1

    def test_chat_share_theme_variants_parse_from_chat_full_info(self):
        """share_theme rides on ChatFullInfo, which stays an unmodelled dict,
        so the union is parsed directly rather than through a parent type."""
        from moonlygram import ChatShareTheme

        emoji_theme = ChatShareTheme.from_dict({
            "type": "emoji",
            "emojis": [
                {"type": "emoji", "emoji": "\N{ROCKET}"},
                {"type": "custom_emoji", "custom_emoji_id": "ce1"},
            ],
            "background_backdrop_id": 3,
        })
        assert emoji_theme.type == "emoji"
        assert emoji_theme.emojis is not None
        assert emoji_theme.emojis[0].emoji == "\N{ROCKET}"
        assert emoji_theme.emojis[1].custom_emoji_id == "ce1"
        assert emoji_theme.background_backdrop_id == 3
        assert emoji_theme.gift is None

        gift_theme = ChatShareTheme.from_dict({
            "type": "unique_gift",
            "gift": {"base_name": "Pepe", "name": "Pepe-1", "number": 1},
        })
        assert gift_theme.gift is not None
        assert gift_theme.gift.name == "Pepe-1"
        assert gift_theme.emojis is None


def test_bot_exposes_every_widget_method():
    """A smoke check that the names are on Bot under their snake_case spelling."""
    for name in (
        "send_widget",
        "send_shared_widget",
        "answer_widget_query",
        "edit_message_widget_data",
        "edit_shared_widget_data",
        "get_chat_share_theme_backdrops",
    ):
        assert callable(getattr(Bot, name))
