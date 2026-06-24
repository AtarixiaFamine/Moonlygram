# Persistence

`bot_data`, `chat_data`, and `user_data` are dictionaries on `context` for keeping state across
updates. By default they live in memory; attach a persistence backend to survive restarts.

```python
from moonlygram.ext import Application, PicklePersistence

app = (
    Application.builder()
    .token("TOKEN")
    .persistence(PicklePersistence("bot.pickle"))
    .build()
)
```

- `DictPersistence` — an in-memory snapshot (handy for tests, or for handing state to another
  store).
- `PicklePersistence("path")` — a single pickle file on disk.

State is **loaded on `initialize`** and **flushed on `shutdown`**, or on demand with
`await app.update_persistence()`. It is snapshot-based: it survives a clean shutdown or an
explicit flush — not a hard crash mid-run.

## Persistent conversations

Give a `ConversationHandler` a `name` and `persistent=True` and its state is stored too:

```python
conv = ConversationHandler(..., name="signup", persistent=True)
```

To back state with your own store (Redis, a database, …), implement the `BasePersistence`
interface.
