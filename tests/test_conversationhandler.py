"""Tests for ConversationHandler."""
from __future__ import annotations

import asyncio

from moonlygram import (
    CallbackQuery,
)
from moonlygram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    TypeHandler,
    filters,
)
from moonlygram.types import Update
from conftest import (
    ASK_AGE,
    ASK_NAME,
    _conv_update,
    fake_bot,
)


class TestConversationHandler:
    async def test_conversation_full_flow_and_reenter(self):
        bot, _ = fake_bot()
        app = Application(bot)
        log: list[str] = []

        async def start(update, context):
            log.append("start")
            return ASK_NAME

        async def got_name(update, context):
            log.append(f"name:{update.message.text}")
            return ASK_AGE

        async def got_age(update, context):
            log.append(f"age:{update.message.text}")
            return ConversationHandler.END

        app.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("start", start)],
                states={
                    ASK_NAME: [MessageHandler(filters.text, got_name)],
                    ASK_AGE: [MessageHandler(filters.text, got_age)],
                },
            )
        )

        await app.process_update(_conv_update("/start"))
        await app.process_update(_conv_update("Alice"))
        await app.process_update(_conv_update("30"))
        await app.process_update(_conv_update("stray"))  # conversation ended: ignored
        await app.process_update(_conv_update("/start"))  # re-enters

        assert log == ["start", "name:Alice", "age:30", "start"]

    async def test_conversation_per_user_isolation(self):
        bot, _ = fake_bot()
        app = Application(bot)
        names: dict[int, str] = {}

        async def start(update, context):
            return ASK_NAME

        async def got_name(update, context):
            names[update.effective_user_id] = update.message.text
            return ConversationHandler.END

        app.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("start", start)],
                states={ASK_NAME: [MessageHandler(filters.text, got_name)]},
            )
        )

        await app.process_update(_conv_update("/start", from_id=1))
        await app.process_update(_conv_update("/start", from_id=2))
        await app.process_update(_conv_update("Alice", from_id=1))
        await app.process_update(_conv_update("Bob", from_id=2))

        assert names == {1: "Alice", 2: "Bob"}

    async def test_conversation_fallback_cancels(self):
        bot, _ = fake_bot()
        app = Application(bot)
        log: list[str] = []

        async def start(update, context):
            return ASK_NAME

        async def got_name(update, context):
            log.append("name")
            return ConversationHandler.END

        async def cancel(update, context):
            log.append("cancel")
            return ConversationHandler.END

        app.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("start", start)],
                states={ASK_NAME: [MessageHandler(filters.text & ~filters.command("cancel"), got_name)]},
                fallbacks=[CommandHandler("cancel", cancel)],
            )
        )

        await app.process_update(_conv_update("/start"))
        await app.process_update(_conv_update("/cancel"))
        await app.process_update(_conv_update("late"))  # ended: ignored

        assert log == ["cancel"]

    async def test_conversation_allow_reentry(self):
        bot, _ = fake_bot()

        async def run(reentry: bool) -> int:
            app = Application(bot)
            starts: list[int] = []

            async def start(update, context):
                starts.append(1)
                return ASK_NAME

            async def got(update, context):
                return ConversationHandler.END

            app.add_handler(
                ConversationHandler(
                    entry_points=[CommandHandler("start", start)],
                    states={ASK_NAME: [MessageHandler(filters.regex("zzz_no_match"), got)]},
                    allow_reentry=reentry,
                )
            )
            await app.process_update(_conv_update("/start"))
            await app.process_update(_conv_update("/start"))  # second entry while in a state
            return len(starts)

        assert await run(False) == 1
        assert await run(True) == 2

    async def test_conversation_coexists_with_groups(self):
        bot, _ = fake_bot()
        app = Application(bot)
        log: list[str] = []

        async def start(update, context):
            log.append("start")
            return ASK_NAME

        async def tap(update, context):
            log.append("tap")

        app.add_handler(
            ConversationHandler(entry_points=[CommandHandler("start", start)], states={ASK_NAME: []}),
            group=0,
        )
        app.add_handler(TypeHandler(tap), group=1)
        await app.process_update(_conv_update("/start"))

        assert log == ["start", "tap"]


class TestConversationHandlerCompletion:
    def test_handler_block_attribute(self):
        async def cb(update, context):
            return None

        assert MessageHandler(filters.all, cb, block=False).block is False
        assert CommandHandler("x", cb).block is True
        assert ConversationHandler(entry_points=[], states={}).block is True

    async def test_conversation_timeout_ends_after_inactivity(self):
        bot, _ = fake_bot()
        app = Application(bot)
        log: list[str] = []

        async def start(update, context):
            return ASK_NAME

        async def got_name(update, context):
            log.append(update.message.text)
            return ConversationHandler.END

        app.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("start", start)],
                states={ASK_NAME: [MessageHandler(filters.text, got_name)]},
                conversation_timeout=0.05,
            )
        )

        await app.process_update(_conv_update("/start"))
        await asyncio.sleep(0.12)  # let the inactivity timer fire
        await app.process_update(_conv_update("Alice"))  # already timed out: ignored

        assert log == []

    async def test_conversation_timeout_resets_on_activity(self):
        bot, _ = fake_bot()
        app = Application(bot)
        log: list[str] = []

        async def start(update, context):
            return ASK_NAME

        async def got_name(update, context):
            log.append("name")
            return ASK_AGE

        async def got_age(update, context):
            log.append("age")
            return ConversationHandler.END

        app.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("start", start)],
                states={
                    ASK_NAME: [MessageHandler(filters.text, got_name)],
                    ASK_AGE: [MessageHandler(filters.text, got_age)],
                },
                conversation_timeout=0.2,
            )
        )

        await app.process_update(_conv_update("/start"))
        await asyncio.sleep(0.05)
        await app.process_update(_conv_update("Alice"))  # resets the timer -> ASK_AGE
        await asyncio.sleep(0.05)
        await app.process_update(_conv_update("30"))  # still within the window

        assert log == ["name", "age"]

    async def test_conversation_per_message_keys_on_message(self):
        bot, _ = fake_bot()
        app = Application(bot)
        entered: list[int] = []
        tapped: list[int] = []

        async def enter(update, context):
            entered.append(update.callback_query.message.message_id)
            return ASK_NAME

        async def tap(update, context):
            tapped.append(update.callback_query.message.message_id)
            return ConversationHandler.END

        app.add_handler(
            ConversationHandler(
                entry_points=[CallbackQueryHandler(enter, pattern="^enter$")],
                states={ASK_NAME: [CallbackQueryHandler(tap, pattern="^tap$")]},
                per_message=True,
            )
        )

        def cq(data: str, message_id: int) -> Update:
            return Update(
                update_id=1,
                callback_query=CallbackQuery.from_dict(
                    {
                        "id": "c",
                        "from": {"id": 1, "is_bot": False, "first_name": "A"},
                        "message": {
                            "message_id": message_id,
                            "chat": {"id": 1, "type": "private"},
                        },
                        "data": data,
                    }
                ),
            )

        await app.process_update(cq("enter", 10))  # start a conversation on message 10
        await app.process_update(cq("tap", 11))  # different message: no conversation
        await app.process_update(cq("tap", 10))  # same message: ends it

        assert entered == [10]
        assert tapped == [10]

    async def test_conversation_map_to_parent_nested(self):
        bot, _ = fake_bot()
        app = Application(bot)
        log: list[str] = []
        parent_menu, child_state = 10, 20

        async def parent_start(update, context):
            log.append("parent_start")
            return child_state

        async def child_start(update, context):
            log.append("child_start")
            return 1

        async def child_done(update, context):
            log.append("child_done")
            return ConversationHandler.END

        async def parent_again(update, context):
            log.append("parent_again")
            return ConversationHandler.END

        child = ConversationHandler(
            entry_points=[CommandHandler("child", child_start)],
            states={1: [CommandHandler("finish", child_done)]},
            map_to_parent={ConversationHandler.END: parent_menu},
        )
        app.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("start", parent_start)],
                states={
                    child_state: [child],
                    parent_menu: [CommandHandler("again", parent_again)],
                },
            )
        )

        await app.process_update(_conv_update("/start"))  # parent -> child_state
        await app.process_update(_conv_update("/child"))  # enter the nested conversation
        await app.process_update(_conv_update("/finish"))  # child END -> parent_menu
        await app.process_update(_conv_update("/again"))  # parent_menu handler runs

        assert log == ["parent_start", "child_start", "child_done", "parent_again"]
