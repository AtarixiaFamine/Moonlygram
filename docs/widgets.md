# Widgets

Bot API 10.4 adds widgets: a block of HTML the Telegram app renders inside a
message bubble. Unlike a rich message, which Telegram parses into its own
structure, a widget's HTML runs as HTML, and it can talk back to the bot.

!!! warning "Private chats only, for now"

    In production Telegram accepts widgets in private chats only. A sent widget
    always has protected content, so it cannot be forwarded, and `copy_message`
    and `copy_messages` refuse a message carrying one. Inline query results
    can describe a widget, but production inline mode does not serve them yet.

## Sending

`send_widget` takes the HTML and returns the sent `Message`.

```python
await bot.send_widget(
    chat_id,
    "<div style='font: 16px sans-serif'>Hello from a widget.</div>",
    width=300,
    height=120,
    caption="A widget",
)
```

`html` is 1-32768 bytes, and must still fit in 4096 bytes once zlib has
compressed it at maximum level. `width` and `height` are logical pixels: the
app clamps the width to 200 or wider and the height to 50-600. Omit either and
the widget sizes itself to the bubble.

### Data

A widget carries two pieces of data, both 0-1024 bytes.

- `public_data` is the same everywhere the widget appears.
- `chat_data` belongs to the one message.

```python
message = await bot.send_widget(
    chat_id,
    html,
    public_data='{"score": 0}',
    chat_data='{"player": "alex"}',
)
```

The sent `Message.widget` reports both back, along with `Widget.id` when the
widget is shared.

## Queries

A widget can only call the bot if the message was sent with
`allow_queries=True`. The call arrives as a `widget_query` update, which
`WidgetQueryHandler` dispatches.

```python
from moonlygram.ext import Application, WidgetQueryHandler


async def on_query(update, context):
    query = update.widget_query
    await query.answer(f"got {query.data}")


app.add_handler(WidgetQueryHandler(on_query))
```

Answer within 15 seconds. Telegram accepts at most 5 queries per 5 seconds from
one user across all of a bot's widgets.

Filter on the query's data with `pattern`, which matches like
`CallbackQueryHandler`'s:

```python
app.add_handler(WidgetQueryHandler(on_roll, pattern="^roll:"))
```

An answer reaches only the widget that asked, and changes nothing the widget
stores. To change what it shows, edit its data:

```python
await update.widget_query.edit_widget_data(public_data='{"score": 1}')
```

`edit_widget_data` finds the message from the query, whether it sits in a chat
or in an inline message. `Bot.edit_message_widget_data` is the unbound form.
An omitted argument leaves that half of the data alone; an empty string clears
it.

### What a query carries

`WidgetQuery.type` says what the widget asked for. All three shapes are one
`WidgetQueryType` object, with the fields the variant does not use left `None`.

| `type` | Carries |
| --- | --- |
| `data` | `wallet_card`, the sender's TON wallet card, if they shared it |
| `sign_data` | `wallet` and `sign_data`, data their wallet signed |
| `sent_transaction` | `wallet` and `msg_hash`, a transaction they sent |

```python
if query.type.type == "sent_transaction":
    await log_payment(query.type.msg_hash, query.type.wallet.address)
```

## Shared widgets

Send a widget with `is_shared=True` and the resulting `Message.widget` has an
`id`. `send_shared_widget` puts that same widget in another message.

```python
first = await bot.send_widget(chat_id, html, is_shared=True, allow_queries=True)
await bot.send_shared_widget(other_chat_id, first.widget.id, chat_data="second")
```

Every copy shares the widget's public data, so one edit changes all of them:

```python
await bot.edit_shared_widget_data(widget_id, '{"score": 2}', cache_time=60)
```

Telegram accepts at most one such change per second. `cache_time` is how long
a client may hold the public data, 5-3600 seconds, defaulting to 30.

A shared widget keeps working after its message is forwarded. A query from one
of those forwarded copies arrives as a `shared_widget_query` update instead,
which names no chat or message:

```python
from moonlygram.ext import SharedWidgetQueryHandler


async def on_shared(update, context):
    query = update.shared_widget_query
    # query.widget_id is all there is to go on; there is no chat to reply in
    await query.answer("thanks")


app.add_handler(SharedWidgetQueryHandler(on_shared))
```

## TON wallet objects

A widget query may carry the sender's wallet, and `ChatFullInfo` carries
`ton_wallet_card` for a user who shows one on their profile. The amounts are
strings in the currency's smallest units, because they do not survive a float.

`TonWalletCard` holds the address, the balance, and the stickers placed on it;
each `TonWalletCardSticker` pairs an `AreaPosition` with the `TonNft` shown
there. `AreaPosition` was called `StoryAreaPosition` before 10.4, which
renamed it now that a wallet card positions stickers the same way a story does.

## Service messages

Two new service messages land on `Message`:

- `ton_wallet_transfer` reports a TON transfer, with a negative `amount` for an
  outgoing one.
- `paid_messages_waived` says the sender used a link that let them message
  without paying Telegram Stars. It holds no fields, so its presence is the
  whole signal.

```python
if update.message.paid_messages_waived is not None:
    ...
```
