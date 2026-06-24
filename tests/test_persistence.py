"""Tests for persistence backends."""
from __future__ import annotations

from moonlygram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    DictPersistence,
    MessageHandler,
    PicklePersistence,
    filters,
)
from conftest import (
    ASK_NAME,
    _conv_update,
    _msg,
    _update,
    fake_bot,
)


_GETME = {"id": 1, "is_bot": True, "first_name": "B", "username": "b"}


async def test_dict_persistence_loads_and_flushes_bot_data():
    persistence = DictPersistence(bot_data={"count": 1})
    bot, _ = fake_bot(_GETME)
    app = Application(bot, persistence=persistence)
    seen: dict[str, int] = {}

    async def handler(update, context):
        seen["count"] = context.bot_data["count"]
        context.bot_data["count"] += 1

    app.add_handler(MessageHandler(filters.all, handler))
    await app.initialize()  # loads bot_data {"count": 1}
    await app.process_update(_update(_msg("hi")))
    assert seen["count"] == 1
    await app.shutdown()  # flushes
    assert persistence.bot_data == {"count": 2}


async def test_conversation_state_persists_across_restart():
    persistence = DictPersistence()

    def build_app() -> Application:
        bot, _ = fake_bot(_GETME)
        app = Application(bot, persistence=persistence)

        async def start(update, context):
            return ASK_NAME

        async def got_name(update, context):
            context.bot_data["name"] = update.message.text
            return ConversationHandler.END

        app.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("start", start)],
                states={ASK_NAME: [MessageHandler(filters.text, got_name)]},
                persistent=True,
                name="onboard",
            )
        )
        return app

    app1 = build_app()
    await app1.initialize()
    await app1.process_update(_conv_update("/start"))  # now mid-conversation
    await app1.shutdown()  # persists conversation state

    app2 = build_app()
    await app2.initialize()  # restores the conversation
    await app2.process_update(_conv_update("Alice"))  # resumes and finishes
    await app2.shutdown()

    assert persistence.bot_data["name"] == "Alice"


async def test_pickle_persistence_round_trip(tmp_path):
    path = str(tmp_path / "state.pkl")

    async def handler(update, context):
        context.bot_data["hits"] = context.bot_data.get("hits", 0) + 1

    bot, _ = fake_bot(_GETME)
    app = Application(bot, persistence=PicklePersistence(path))
    app.add_handler(MessageHandler(filters.all, handler))
    await app.initialize()
    await app.process_update(_update(_msg("a")))
    await app.process_update(_update(_msg("b")))
    await app.shutdown()  # writes the file

    bot2, _ = fake_bot(_GETME)
    app2 = Application(bot2, persistence=PicklePersistence(path))
    await app2.initialize()
    assert app2.bot_data == {"hits": 2}
    await app2.shutdown()


async def test_builder_persistence():
    persistence = DictPersistence()
    app = Application.builder().token("123:fake").persistence(persistence).build()
    try:
        assert app.persistence is persistence
    finally:
        await app.shutdown()
