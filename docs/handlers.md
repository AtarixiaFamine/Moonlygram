# Handlers and filters

An `Application` routes each incoming `Update` to the handlers you register. A handler pairs a
*check* (does this update match?) with an `async` callback that takes `(update, context)`.

## Registering handlers

```python
from moonlygram.ext import Application, CommandHandler, MessageHandler, filters

app = Application.builder().token("TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.text & ~filters.regex(r"^/"), echo))
```

The handler types:

- `CommandHandler("name", cb)` — `/name` (and `/name@bot`).
- `PrefixHandler("!", "name", cb)` — a custom prefix.
- `MessageHandler(filter, cb)` — any message matching a filter.
- `CallbackQueryHandler(cb, pattern="^...$")` — inline-button taps.
- `InlineQueryHandler`, `ChosenInlineResultHandler` — inline mode.
- `ChatMemberHandler`, `ChatJoinRequestHandler` — membership changes.
- `PollHandler`, `PollAnswerHandler`, `MessageReactionHandler`, `ChatBoostHandler`.
- `TypeHandler(Update, cb)` — every update (or a predicate).
- `ConversationHandler` — multi-step flows (see [Conversations](conversations.md)).

## Filters

Filters decide which messages a `MessageHandler` runs for. They are lowercase and combine with
`&` (and), `|` (or), and `~` (not):

```python
MessageHandler(filters.photo | filters.video, on_media)
MessageHandler(filters.command("ban") & filters.group, on_ban)
MessageHandler(filters.text & ~filters.regex(r"^/"), echo)
```

Singletons include `text`, `private`, `group`, `channel`, `reply`, `forwarded`, `photo`,
`document`, `audio`, `video`, `animation`, `voice`, `video_note`, `sticker`, `location`,
`venue`, `contact`, `poll`, `dice`. Parameterised ones include `command(...)`, `regex(...)`,
`caption_regex(...)`, `user(...)`, `chat(...)`, `username(...)`, `entity(...)`, and
`mime_type(...)`. See the [filters reference](api/filters.md) for the full set.

## Handler groups

`add_handler(handler, group=N)` puts a handler in a numbered group. Within a group the **first**
matching handler runs; across groups, **every** group gets a turn (in ascending order). Raise
`ApplicationHandlerStop` from a handler to stop all further processing for that update.

```python
app.add_handler(TypeHandler(Update, log_update), group=-1)  # runs first, for every update
app.add_handler(CommandHandler("start", start), group=0)
```

## The context

The second argument carries the call surface and your state: `context.bot`, `context.args` (a
command's arguments), `context.user_data` / `context.chat_data` / `context.bot_data` (see
[Persistence](persistence.md)), and `context.job_queue`. Register an error handler with
`app.add_error_handler(cb)`; the exception is then available as `context.error`.
