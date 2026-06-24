# Migrating from python-telegram-bot

Moonlygram was built to mirror python-telegram-bot's (ptb) shape, so porting an
existing bot is mostly mechanical. The classes, the builder, the
`(update, context)` callback signature, and the bound shortcuts
(`update.message.reply_text(...)`) all carry the same names. For a typical bot
the move takes minutes; the only hard blocker is a bot that depends on a domain
Moonlygram has not implemented yet (see [What isn't ported yet](#what-isnt-ported-yet)).

## 1. Change the import root

Two find-and-replace passes cover almost every file:

| python-telegram-bot | Moonlygram |
| --- | --- |
| `from telegram import ...` | `from moonlygram import ...` |
| `from telegram.ext import ...` | `from moonlygram.ext import ...` |

The names you import are the same: `Bot`, `Update`, `Message`, `Chat`, `User`,
`InlineKeyboardButton`/`InlineKeyboardMarkup`, `Application`,
`ApplicationBuilder`, `CommandHandler`, `MessageHandler`,
`CallbackQueryHandler`, `ConversationHandler`, `Defaults`, `ContextTypes`,
`JobQueue`, `AIORateLimiter`, `BasePersistence` / `DictPersistence` /
`PicklePersistence`, and so on.

## 2. Lowercase the filters

This is the one real gotcha. ptb exposes filters as **uppercase** constants and
**capitalized** factory classes; Moonlygram uses **lowercase** names throughout.

| python-telegram-bot | Moonlygram |
| --- | --- |
| `filters.TEXT` | `filters.text` |
| `filters.PHOTO` | `filters.photo` |
| `filters.VIDEO` | `filters.video` |
| `filters.Document.ALL` | `filters.document` |
| `filters.ChatType.PRIVATE` | `filters.private` |
| `filters.ChatType.GROUPS` | `filters.group` |
| `filters.Regex("...")` | `filters.regex("...")` |
| `filters.CaptionRegex("...")` | `filters.caption_regex("...")` |
| `filters.User(123)` | `filters.user(123)` |
| `filters.Chat(123)` | `filters.chat(123)` |

The combinators are identical — `&`, `|`, and `~` all work the same way.

One shape difference worth knowing: ptb's bare `filters.COMMAND` (match *any*
command) has no direct constant. In Moonlygram, `filters.command("start")` takes
the command name(s). For "any message that is a command," use
`filters.regex(r"^/")`:

```python
# ptb:        MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
# Moonlygram:
MessageHandler(filters.text & ~filters.regex(r"^/"), echo)
```

## 3. Everything else is the same

These carry over unchanged:

- **Building the app** — `Application.builder().token("...").build()`.
- **Callbacks** — `async def handler(update, context): ...`.
- **Bound shortcuts** — `update.message.reply_text(...)`,
  `update.callback_query.answer(...)`, `update.callback_query.edit_message_text(...)`.
- **Defaults** — `Defaults(parse_mode=..., protect_content=...)` on the builder.
- **Conversations** — `ConversationHandler(entry_points=..., states=..., fallbacks=...)`,
  `ConversationHandler.END`, `conversation_timeout`, `per_message`, and nested
  `map_to_parent`.
- **Persistence** — `.persistence(PicklePersistence("bot.pickle"))` on the
  builder; `bot_data` / `chat_data` / `user_data` and persistent conversation
  state load on `initialize` and flush on `shutdown`.
- **JobQueue** — `context.job_queue.run_repeating(...)` /
  `run_once` / `run_daily` / `run_monthly`.
- **Rate limiting** — `.rate_limiter(AIORateLimiter(...))`.
- **Context types** — `.context_types(ContextTypes(context=..., bot_data=...))`.

### Before / after

```python
# python-telegram-bot
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

app = Application.builder().token("TOKEN").build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.run_polling()
```

```python
# Moonlygram
from moonlygram import Update
from moonlygram.ext import Application, CommandHandler, MessageHandler, filters

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

app = Application.builder().token("TOKEN").build()
app.add_handler(MessageHandler(filters.text & ~filters.regex(r"^/"), echo))
app.run_polling()
```

## What you gain

`send_rich_message` (Bot API 10.1) has no ptb equivalent — block-level structure
(headings, tables, collapsibles, math) built with the `moonlygram.rich`
helpers. See [Rich messages](rich-messages.md).

## What isn't ported yet

Moonlygram is a pure Bot API HTTP client (no MTProto), exactly like ptb, so the
account-level features ptb also lacks are out of scope. Within the Bot API, a
few **niche domains are still in progress** — a bot that relies on these can't
move over until they land:

- Payments / Telegram Stars
- Business accounts and connections
- Games
- Passport, giveaways, and paid media

Everything else — messaging and editing, media, albums, chat and member
administration, bot configuration, forum topics, stickers, and inline mode — is
already covered. If you hit an unmodelled method in the meantime, the escape
hatch `bot.call("anyMethod", **params)` reaches it directly.
