# Conversations

`ConversationHandler` runs a multi-step flow as a state machine, keyed per chat and user. Entry
points start a conversation; each callback returns the next state — or `ConversationHandler.END`
to finish.

```python
from moonlygram.ext import (
    Application, CommandHandler, ConversationHandler, MessageHandler, filters,
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
    await update.message.reply_text(f"Hi {context.user_data['name']}!")
    return ConversationHandler.END


async def cancel(update, context):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NAME: [MessageHandler(filters.text & ~filters.command("cancel"), got_name)],
        AGE: [MessageHandler(filters.text & ~filters.command("cancel"), got_age)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
app.add_handler(conv)
```

## Options

- `conversation_timeout=seconds` — end the conversation after that much inactivity.
- `allow_reentry=True` — let an entry point restart an in-progress conversation.
- `per_chat` / `per_user` / `per_message` — change the conversation key. It defaults to
  `(chat, user)`; `per_message` also keys on the message, for callback-query-only flows.
- `map_to_parent={...}` — when nested inside another conversation, map a child's returned state
  back onto a parent state.
- `persistent=True` with `name="..."` — keep the conversation across restarts (see
  [Persistence](persistence.md)).
