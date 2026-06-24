"""Send a Bot API 10.1 rich message — the library's headline feature.

    BOT_TOKEN=123:abc python examples/richbot.py
"""
import os

from moonlygram import RichMessage
from moonlygram.ext import Application, CommandHandler
from moonlygram.rich import bold, code, link


async def show(update, context):
    msg = (
        RichMessage()
        .heading("Moonlygram")
        .paragraph("A rich message with ", bold("bold"), ", ", code("code"), ", and a ",
                   link("link", "https://example.com"), ".")
        .code_block("await bot.send_rich_message(chat_id, html=msg)", language="python")
        .quote("Built on Bot API 10.1.")
    )
    await context.bot.send_rich_message(update.effective_chat_id, html=msg)


def main() -> None:
    app = Application.builder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("rich", show))
    app.run_polling()


if __name__ == "__main__":
    main()
