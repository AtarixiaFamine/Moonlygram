# Quickstart

## Run a polling bot

`run_polling()` owns the event loop and shuts down cleanly on Ctrl-C. Receiving
and dispatch run concurrently, so a slow handler never stalls the next update.

```python
from moonlygram.ext import Application, CommandHandler, MessageHandler, filters


async def start(update, context):
    await update.message.reply_text("Send me anything.")


async def echo(update, context):
    await update.message.reply_text(update.message.text)


app = Application.builder().token("YOUR_BOT_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.text & ~filters.command("start"), echo))
app.run_polling()
```

## Embed in an existing loop

Use the async primitives directly when you already run an event loop:

```python
async with app:
    await app.start_polling()
    ...
```

`initialize()` / `start_polling()` / `shutdown()` are also available
individually.

## Webhooks

Use the built-in server:

```python
app.run_webhook(
    port=8443,
    url_path="hook",
    webhook_url="https://example.com/hook",
    secret_token="…",
)
```

…or feed updates from your own web framework with
`app.feed_webhook_update(data)`.

## Filters

Filters select which messages a `MessageHandler` runs for, and combine with
`&`, `|`, and `~`:

```python
from moonlygram.ext import filters

MessageHandler(filters.photo | filters.video, on_media)
MessageHandler(filters.command("ban") & filters.group, on_ban)
```

See the [filters reference](api/filters.md) for the full set.
