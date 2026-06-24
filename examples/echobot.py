"""The smallest useful bot: echo back any text message.

Run with your bot token in the environment:

    BOT_TOKEN=123:abc python examples/echobot.py
"""
import os

from moonlygram.ext import Application, CommandHandler, MessageHandler, filters


async def start(update, context):
    await update.message.reply_text("Send me anything and I'll echo it back.")


async def echo(update, context):
    await update.message.reply_text(update.message.text)


def main() -> None:
    app = Application.builder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.text & ~filters.command("start"), echo))
    app.run_polling()


if __name__ == "__main__":
    main()
