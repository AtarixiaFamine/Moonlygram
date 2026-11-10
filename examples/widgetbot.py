"""Send a widget and answer the queries it raises (Bot API 10.4).

    BOT_TOKEN=123:abc python examples/widgetbot.py

/widget sends an HTML widget that may call back to the bot; /shared sends a
shared one and then resends the same widget in a second message, which is what
a widget_id is for. Queries arrive through WidgetQueryHandler.

Production Telegram accepts widgets in private chats only, so send these to the
bot in a direct chat.

The HTML below only renders. Raising a query is the widget's own side of the
conversation, through the in-app bridge Telegram documents with the widget
format itself rather than in the Bot API schema; the handler here answers
whatever arrives.
"""
import os

from moonlygram.ext import Application, CommandHandler, WidgetQueryHandler

WIDGET_HTML = """
<div style="font: 15px -apple-system, sans-serif; padding: 12px;
            border-radius: 12px; background: #f1f3f5; color: #1a1a1a">
  <div style="font-weight: 600; margin-bottom: 4px">Moonlygram</div>
  <div>A widget is HTML the app renders inside the bubble.</div>
</div>
"""


async def send_widget(update, context):
    message = await context.bot.send_widget(
        update.effective_chat_id,
        WIDGET_HTML,
        height=96,
        public_data='{"taps": 0}',
        caption="An HTML widget",
        allow_queries=True,
    )
    # The sent message carries the widget back. Without is_shared it has no
    # id, so there is nothing for send_shared_widget to reuse.
    print("widget id:", message.widget.id)


async def send_shared(update, context):
    first = await context.bot.send_widget(
        update.effective_chat_id,
        WIDGET_HTML,
        height=96,
        public_data='{"taps": 0}',
        is_shared=True,
        allow_queries=True,
    )
    widget_id = first.widget.id
    await context.bot.send_shared_widget(
        update.effective_chat_id,
        widget_id,
        chat_data='{"copy": 2}',
        caption="The same widget again",
    )
    # One edit changes the public data of both messages.
    await context.bot.edit_shared_widget_data(widget_id, '{"taps": 1}')


async def on_query(update, context):
    query = update.widget_query
    # Answer within 15 seconds. This reaches only the widget that asked.
    await query.answer(f"received {query.data!r}")
    # Changing what everyone sees is a separate edit.
    await query.edit_widget_data(chat_data='{"last": "' + query.data + '"}')


def main() -> None:
    app = Application.builder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("widget", send_widget))
    app.add_handler(CommandHandler("shared", send_shared))
    app.add_handler(WidgetQueryHandler(on_query))
    app.run_polling()


if __name__ == "__main__":
    main()
