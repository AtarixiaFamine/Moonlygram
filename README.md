<p align="center">
  <a href="https://github.com/AtarixiaFamine/Moonlygram">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/AtarixiaFamine/Moonlygram/main/docs/logo-white.png">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/AtarixiaFamine/Moonlygram/main/docs/logo-black.png">
      <img alt="Moonlygram Logo" width="128" src="https://raw.githubusercontent.com/AtarixiaFamine/Moonlygram/main/docs/logo-black.png">
    </picture>
  </a>
</p>

<h1 align="center">Moonlygram</h1>

<p align="center">
  <b>A modern, async Python framework for the Telegram Bot API, with built-in rich messages.</b>
  <br>
  Pure HTTP. No MTProto. No native dependencies.
</p>

<p align="center">
  <a href="https://pypi.org/project/moonlygram/"><img src="https://img.shields.io/pypi/v/moonlygram.svg" alt="PyPI"></a>
  <img src="https://img.shields.io/pypi/pyversions/moonlygram.svg" alt="Python versions">
  <img src="https://img.shields.io/badge/mypy-strict-blue.svg" alt="mypy strict">
  <img src="https://img.shields.io/badge/Bot%20API-10.1-2CA5E0.svg" alt="Bot API 10.1">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"></a>
</p>

---

## Description

**Moonlygram** is an asynchronous framework for the Telegram **Bot API**. A `Bot` holds the API
methods and an `Application` (`moonlygram.ext`) registers handlers and runs the update loop, so
the shape feels familiar if you have used [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).
On top of that, it adds something no other library has: **rich messages** (Bot API 10.1).

## Installation

```bash
pip install moonlygram
```

Requires Python 3.10 or newer.

## Usage

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

## Features

- **Familiar:** a python-telegram-bot-style API: `Application`, handlers, filters, and
  `(update, context)` callbacks. Existing bots port with little more than renamed imports.
- **Async:** receiving and dispatch run concurrently, so a slow handler never stalls the next
  update.
- **Performant:** a non-blocking poll loop, optional parallel dispatch, a built-in rate limiter,
  and a dependency-free `JobQueue`.
- **Rich:** send Bot API 10.1 rich messages (headings, tables, collapsibles, math) with a
  composable, auto-escaping builder, or convert Markdown in one call. No other library has this.
- **Type-hinted:** ships `py.typed` and passes `mypy --strict`. The received types are generated
  from the Bot API schema, so they cannot silently drift.
- **Lightweight:** one dependency (`httpx`). Pure HTTP, with no MTProto, no `api_id`/`api_hash`,
  and no C extensions.
- **Batteries included:** conversations, persistence, scheduled jobs, arbitrary callback data,
  and both polling and webhooks.

## Resources

- **Documentation:** https://atarixiafamine.github.io/Moonlygram/
- **Migrating from python-telegram-bot:** https://atarixiafamine.github.io/Moonlygram/migrating/
- **Examples:** [`examples/`](examples/)
- **Changelog:** [`CHANGELOG.md`](CHANGELOG.md)

## Roadmap

Core messaging, media, chat and member administration, bot configuration, forum topics,
stickers, and inline mode are all covered. Still in progress: the niche Bot API domains of
payments / Telegram Stars, business accounts, games, and passport / giveaways / paid media.

## Contributing

Contributions are welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md); it covers the spec-driven
codegen workflow for data types (edit the spec or overrides, regenerate, then test).

## License

Released under the **MIT License**. See [`LICENSE`](LICENSE). Copyright © 2026 AtarixiaFamine.
