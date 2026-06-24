# Performance

Moonlygram is built to feel like a modern async library. Several of its defaults and knobs are
about throughput.

## Non-blocking by default

`run_polling()` receives updates and dispatches them concurrently through an internal queue, so a
slow handler never stalls `getUpdates`. The poll loop retries transient network and API errors
with exponential backoff (a bad token still fails fast).

## Concurrent dispatch

By default updates are processed one at a time. Opt into parallelism:

```python
app = Application.builder().token("TOKEN").concurrent_updates(True).build()
```

`concurrent_updates(True)` allows up to 256 updates in flight (pass an `int` for a custom cap,
with backpressure when it is reached). For a single slow handler, set `block=False` on it so
later groups aren't delayed while it runs in the background:

```python
app.add_handler(MessageHandler(filters.photo, slow_ocr, block=False))
```

## Rate limiting

Telegram throttles bots. `AIORateLimiter` paces outgoing calls and retries on `FloodWait`:

```python
from moonlygram.ext import AIORateLimiter

app = (
    Application.builder()
    .token("TOKEN")
    .rate_limiter(AIORateLimiter(overall_max_rate=30, per_chat_max_rate=1))
    .build()
)
```

It enforces a global cap (default 30 calls/second) and a per-chat cap (default 1/second),
spacing calls evenly rather than letting them burst.

## Arbitrary callback data

Inline buttons normally carry a short `callback_data` string. Enable arbitrary callback data to
attach any Python object instead — it is sent as a short token and resolved back to the object on
the incoming `CallbackQuery`:

```python
app = Application.builder().token("TOKEN").arbitrary_callback_data(True).build()

button = InlineKeyboardButton("Open", callback_data={"action": "open", "id": 42})
```

The token map is a bounded LRU cache, so old entries are evicted automatically.
