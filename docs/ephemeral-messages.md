# Ephemeral messages

Bot API 10.2 adds ephemeral messages: a message a bot sends into a group that
only one specific user and the bot can see. The bot chooses the recipient with
`receiver_user_id`, or answers a callback query with an ephemeral message using
`callback_query_id`.

## Sending

`receiver_user_id` and `callback_query_id` are available on `send_message` and
the other common send methods.

```python
await bot.send_message(
    chat_id,
    "Only you can see this.",
    receiver_user_id=user_id,
)
```

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

## Replying

To reply to an incoming ephemeral message, pass `reply_parameters` with its
`ephemeral_message_id`. A reply to an ephemeral message must itself be
ephemeral, and it must be sent within 15 seconds.

```python
from moonlygram import ReplyParameters

await bot.send_message(
    chat_id,
    "Replying just to you.",
    receiver_user_id=user_id,
    reply_parameters=ReplyParameters(ephemeral_message_id=incoming_id),
)
```

An incoming ephemeral message carries `Message.receiver_user` and
`Message.ephemeral_message_id`.
