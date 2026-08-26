# Ephemeral messages

Bot API 10.2 adds ephemeral messages: a message a bot sends into a group that
only one specific user and the bot can see. Bot API 10.3 reshaped how the
recipient is named, gathering the arguments into `EphemeralMessageParameters`.

## Sending

Pass `ephemeral_message_parameters` to `send_message` or any of the other
common send methods, including `send_rich_message`.

```python
from moonlygram import EphemeralMessageParameters

await bot.send_message(
    chat_id,
    "Only you can see this.",
    ephemeral_message_parameters=EphemeralMessageParameters(
        receiver_user_id=user_id
    ),
)
```

Set `callback_query_id` to answer a callback query with the message, and
`replace_callback_query_message` to show it in place of the message the button
was attached to rather than as a new one.

```python
await bot.send_message(
    chat_id,
    "Only you can see this.",
    ephemeral_message_parameters=EphemeralMessageParameters(
        receiver_user_id=query.from_user.id,
        callback_query_id=query.id,
        replace_callback_query_message=True,
    ),
)
```

### Upgrading from 0.4

Before 10.3 the recipient was given as two flat arguments, `receiver_user_id`
and `callback_query_id`. Telegram no longer reads them, and as of 1.3.0 neither
does Moonlygram: passing either raises `TypeError`. Wrap them instead.

```python
# 0.4
await bot.send_message(chat_id, text, receiver_user_id=uid, callback_query_id=qid)

# 1.3
await bot.send_message(
    chat_id,
    text,
    ephemeral_message_parameters=EphemeralMessageParameters(
        receiver_user_id=uid, callback_query_id=qid
    ),
)
```

The `TypeError` is deliberate: had the arguments been quietly accepted and
ignored, the message would have gone out publicly instead of to one user.

## Editing and deleting

An ephemeral message is identified by its chat, the recipient, and its
`ephemeral_message_id`. Each method returns `True` on success. The recipient may
miss the change if they are offline.

```python
await bot.edit_ephemeral_message_text(
    chat_id, receiver_user_id, ephemeral_message_id, "Updated text."
)
await bot.delete_ephemeral_message(chat_id, receiver_user_id, ephemeral_message_id)
```

The companion methods are `edit_ephemeral_message_media`,
`edit_ephemeral_message_caption`, and `edit_ephemeral_message_reply_markup`.
`edit_ephemeral_message_media` takes a new upload as of 10.3: put an `InputFile`
in the media object, or reference an existing file by `file_id` or URL.

```python
from moonlygram import InputFile, InputMediaPhoto

await bot.edit_ephemeral_message_media(
    chat_id,
    receiver_user_id,
    ephemeral_message_id,
    InputMediaPhoto(InputFile("chart.png"), caption="Updated chart."),
)
```

Give the media a caption. Telegram rejects a caption-less edit here with
`MESSAGE_EMPTY`, whether the file is uploaded or referenced by `file_id` or
URL. The Bot API does not document this, and the other edit methods do not
behave the same way.

To replace the text with rich content, use
`edit_ephemeral_rich_message_text`, which takes the same `html` / `markdown` /
`blocks` forms as `send_rich_message`.

```python
await bot.edit_ephemeral_rich_message_text(
    chat_id, receiver_user_id, ephemeral_message_id, markdown="**Done.**"
)
```

## Replying

To reply to an incoming ephemeral message, pass `reply_parameters` with its
`ephemeral_message_id`. A reply to an ephemeral message must itself be
ephemeral, and it must be sent within 15 seconds.

```python
from moonlygram import EphemeralMessageParameters, ReplyParameters

await bot.send_message(
    chat_id,
    "Replying just to you.",
    ephemeral_message_parameters=EphemeralMessageParameters(
        receiver_user_id=user_id
    ),
    reply_parameters=ReplyParameters(ephemeral_message_id=incoming_id),
)
```

An incoming ephemeral message carries `Message.receiver_user` and
`Message.ephemeral_message_id`.
