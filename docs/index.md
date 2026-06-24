# Moonlygram

An async Telegram **Bot API** client. Pure HTTP, with no MTProto and no native
dependencies. It covers the Bot API surface, including the Bot API 10.1 rich
messages.

A `Bot` holds the API methods, and an `Application` (in `moonlygram.ext`)
registers handlers and runs the update loop. If you have used
python-telegram-bot, the shape will feel familiar.

## Install

```bash
pip install moonlygram
```

## At a glance

```python
from moonlygram import InlineKeyboardButton, InlineKeyboardMarkup
from moonlygram.ext import Application, CallbackQueryHandler, CommandHandler


async def start(update, context):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Tap me", callback_data="tapped")]])
    await update.message.reply_text("Hello from Moonlygram!", reply_markup=keyboard)


async def on_tap(update, context):
    await update.callback_query.answer("You tapped it!")


app = Application.builder().token("YOUR_BOT_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(on_tap, pattern="^tapped$"))

app.run_polling()
```

## Where to go next

- [Quickstart](quickstart.md) — build and run a bot end to end.
- [Rich messages](rich-messages.md) — sending Bot API 10.1 rich content.
- [API reference](api/bot.md) — every public class and method.
