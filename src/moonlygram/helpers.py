"""Small text and link utilities.

These mirror the helpers in python-telegram-bot's telegram.helpers: escaping
text for the Markdown parse modes, building user mentions, constructing deep-
linking start URLs, and naming a message's content type. They are plain
functions with no dependency on a running Bot.
"""
from __future__ import annotations

import re
from html import escape
from typing import Any, Optional

# Message content fields checked by effective_message_type, in priority order.
_MESSAGE_TYPES = (
    "text",
    "animation",
    "audio",
    "document",
    "photo",
    "sticker",
    "video",
    "video_note",
    "voice",
    "contact",
    "dice",
    "location",
    "venue",
    "poll",
    "new_chat_members",
    "left_chat_member",
    "pinned_message",
)


def escape_markdown(
    text: str, version: int = 1, entity_type: Optional[str] = None
) -> str:
    """Escape the Markdown-special characters in text.

    version selects the parse mode: 1 for legacy Markdown, 2 for MarkdownV2.
    For MarkdownV2, entity_type narrows the escaping when the text sits inside
    a code/pre block ("pre"/"code") or a link ("text_link"/"custom_emoji"),
    where Telegram only treats a couple of characters as special.
    """
    if int(version) == 1:
        escape_chars = r"_*`["
    elif entity_type in ("pre", "code"):
        escape_chars = r"\`"
    elif entity_type in ("text_link", "custom_emoji"):
        escape_chars = r"\)"
    else:
        escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


def mention_html(user_id: int | str, name: str) -> str:
    """Return an HTML mention of the user, with name HTML-escaped."""
    return f'<a href="tg://user?id={user_id}">{escape(name)}</a>'


def mention_markdown(user_id: int | str, name: str, version: int = 1) -> str:
    """Return a Markdown mention of the user.

    For version 2 (MarkdownV2) the name is escaped; for version 1 it is left
    as given, matching legacy Markdown.
    """
    tg_link = f"tg://user?id={user_id}"
    if int(version) == 1:
        return f"[{name}]({tg_link})"
    return f"[{escape_markdown(name, version=version)}]({tg_link})"


def create_deep_linked_url(
    bot_username: str, payload: Optional[str] = None, group: bool = False
) -> str:
    """Build a https://t.me start link that opens the bot with a payload.

    With group=True the link uses startgroup, so tapping it offers to add the
    bot to a group and passes the payload on the first interaction there. The
    payload is limited to 64 characters from A-Z, a-z, 0-9, _ and -.
    """
    if bot_username is None or len(bot_username) <= 3:
        raise ValueError("You must provide a valid bot_username.")
    base_url = f"https://t.me/{bot_username}"
    if not payload:
        return base_url
    if len(payload) > 64:
        raise ValueError("The deep-linking payload must not exceed 64 characters.")
    if not re.match(r"^[A-Za-z0-9_-]+$", payload):
        raise ValueError(
            "Only the following characters are allowed for deep-linked "
            "URLs: A-Z, a-z, 0-9, _ and -"
        )
    key = "startgroup" if group else "start"
    return f"{base_url}?{key}={payload}"


def effective_message_type(entity: Any) -> Optional[str]:
    """Name the content type of a Message (or the message inside an Update).

    Returns the first matching content field — "text", "photo", "sticker", and
    so on — or None if the message carries none of the known types.
    """
    message = entity.effective_message if hasattr(entity, "effective_message") else entity
    if message is None:
        return None
    for name in _MESSAGE_TYPES:
        if getattr(message, name, None) is not None:
            return name
    return None
