"""Answer inline queries (type @yourbot <text> in any chat).

Inline mode must be enabled for the bot via @BotFather.

    BOT_TOKEN=123:abc python examples/inlinebot.py
"""
import os

from moonlygram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from moonlygram.ext import Application, InlineQueryHandler


async def inline(update, context):
    query = update.inline_query.query or "nothing"
    await update.inline_query.answer(
        [
            InlineQueryResultArticle(
                id="echo",
                title="Echo",
                input_message_content=InputTextMessageContent(message_text=query),
                description=f"Send: {query}",
            )
        ]
    )


def main() -> None:
    app = Application.builder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(InlineQueryHandler(inline))
    app.run_polling()


if __name__ == "__main__":
    main()
