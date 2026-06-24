"""A multi-step conversation: ask for a name, then an age, then summarise.

    BOT_TOKEN=123:abc python examples/conversationbot.py
"""
import os

from moonlygram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

NAME, AGE = range(2)


async def start(update, context):
    await update.message.reply_text("What's your name?")
    return NAME


async def got_name(update, context):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("How old are you?")
    return AGE


async def got_age(update, context):
    name = context.user_data["name"]
    await update.message.reply_text(f"Nice to meet you, {name} ({update.message.text}).")
    return ConversationHandler.END


async def cancel(update, context):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


def main() -> None:
    app = Application.builder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                NAME: [MessageHandler(filters.text & ~filters.command("cancel"), got_name)],
                AGE: [MessageHandler(filters.text & ~filters.command("cancel"), got_age)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
    )
    app.run_polling()


if __name__ == "__main__":
    main()
