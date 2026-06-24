"""Message filters for MessageHandler.

A filter decides whether a handler runs for a given Message. Filters are Filter
instances and combine with ``&`` (and), ``|`` (or) and ``~`` (not)::

    filters.command("ban") & filters.group

Any callable Message -> bool also works as a predicate, but only Filter
instances support the combinator operators.
"""
from __future__ import annotations

import re
from typing import Callable

from ..types import Message

Predicate = Callable[[Message], bool]


class Filter:
    """A predicate over a Message that supports ``&``, ``|`` and ``~``.

    Args:
        predicate: Callable returning whether the message matches.
        name: Label used in repr, for debugging.
    """

    __slots__ = ("_predicate", "name")

    def __init__(self, predicate: Predicate, name: str = "Filter") -> None:
        self._predicate = predicate
        self.name = name

    def __call__(self, message: Message) -> bool:
        return bool(self._predicate(message))

    def __and__(self, other: "Filter") -> "Filter":
        return Filter(lambda m: self(m) and other(m), f"<{self.name} & {other.name}>")

    def __or__(self, other: "Filter") -> "Filter":
        return Filter(lambda m: self(m) or other(m), f"<{self.name} | {other.name}>")

    def __invert__(self) -> "Filter":
        return Filter(lambda m: not self(m), f"<~{self.name}>")

    def __repr__(self) -> str:
        return self.name


def command(*names: str) -> Filter:
    """Match ``/name`` or ``/name@botusername`` at the start of a message.

    Pass one or more command names; the filter matches any of them.
    """
    wanted = set(names)

    def predicate(message: Message) -> bool:
        if not message.text:
            return False
        first = message.text.split(maxsplit=1)[0]
        if not first.startswith("/"):
            return False
        return first[1:].split("@", 1)[0] in wanted

    return Filter(predicate, f"command({', '.join(names)})")


def regex(pattern: str | re.Pattern[str]) -> Filter:
    """Match messages whose text the regular expression finds (re.search)."""
    compiled = re.compile(pattern)
    return Filter(
        lambda m: m.text is not None and compiled.search(m.text) is not None,
        f"regex({compiled.pattern!r})",
    )


def caption_regex(pattern: str | re.Pattern[str]) -> Filter:
    """Match messages whose caption the regular expression finds (re.search)."""
    compiled = re.compile(pattern)
    return Filter(
        lambda m: m.caption is not None and compiled.search(m.caption) is not None,
        f"caption_regex({compiled.pattern!r})",
    )


def user(*user_ids: int) -> Filter:
    """Match messages sent by any of the given user ids."""
    wanted = set(user_ids)
    return Filter(
        lambda m: m.from_user is not None and m.from_user.id in wanted,
        f"user({', '.join(map(str, user_ids))})",
    )


def chat(*chat_ids: int) -> Filter:
    """Match messages in any of the given chat ids."""
    wanted = set(chat_ids)
    return Filter(
        lambda m: m.chat.id in wanted,
        f"chat({', '.join(map(str, chat_ids))})",
    )


def _strip_at(name: str) -> str:
    return name[1:] if name.startswith("@") else name


def username(*usernames: str) -> Filter:
    """Match messages whose sender has one of the usernames (with or without @)."""
    wanted = {_strip_at(name) for name in usernames}
    return Filter(
        lambda m: m.from_user is not None and m.from_user.username in wanted,
        f"username({', '.join(usernames)})",
    )


def chat_username(*usernames: str) -> Filter:
    """Match messages whose chat has one of the usernames (with or without @)."""
    wanted = {_strip_at(name) for name in usernames}
    return Filter(
        lambda m: m.chat.username in wanted,
        f"chat_username({', '.join(usernames)})",
    )


def forwarded_from(*ids: int) -> Filter:
    """Match messages forwarded from any of the given user or chat ids.

    Matches the original sender recorded in forward_origin, whether that is a
    user, a sender chat, or a channel.
    """
    wanted = set(ids)

    def predicate(message: Message) -> bool:
        origin = message.forward_origin
        if origin is None:
            return False
        for source in (origin.sender_user, origin.sender_chat, origin.chat):
            if source is not None and source.id in wanted:
                return True
        return False

    return Filter(predicate, f"forwarded_from({', '.join(map(str, ids))})")


def entity(*types: str) -> Filter:
    """Match messages carrying a text entity of any of the given types.

    Types are the Bot API entity strings, such as "url", "mention", or "hashtag".
    """
    wanted = set(types)
    return Filter(
        lambda m: any(e.type in wanted for e in (m.entities or ())),
        f"entity({', '.join(types)})",
    )


def mime_type(*types: str) -> Filter:
    """Match a document, audio, video, animation, or voice with one of the mime types."""
    wanted = set(types)

    def predicate(message: Message) -> bool:
        for media in (
            message.document,
            message.audio,
            message.video,
            message.animation,
            message.voice,
        ):
            if media is not None and media.mime_type in wanted:
                return True
        return False

    return Filter(predicate, f"mime_type({', '.join(types)})")


#: Match any message.
all = Filter(lambda _m: True, "all")

#: Match messages that carry text.
text = Filter(lambda m: m.text is not None, "text")

#: Match messages sent in a private (one-on-one) chat.
private = Filter(lambda m: m.chat.type == "private", "private")

#: Match messages sent in a group or supergroup.
group = Filter(lambda m: m.chat.type in ("group", "supergroup"), "group")

#: Match messages sent in a channel.
channel = Filter(lambda m: m.chat.type == "channel", "channel")

#: Match messages that reply to another message.
reply = Filter(lambda m: m.reply_to_message is not None, "reply")

#: Match messages forwarded from another chat or user.
forwarded = Filter(lambda m: m.forward_origin is not None, "forwarded")

#: Match messages sent via an inline bot.
via_bot = Filter(lambda m: m.via_bot is not None, "via_bot")

#: Match messages that contain a photo.
photo = Filter(lambda m: m.photo is not None, "photo")

#: Match messages that contain a document.
document = Filter(lambda m: m.document is not None, "document")

#: Match messages that contain an audio file.
audio = Filter(lambda m: m.audio is not None, "audio")

#: Match messages that contain a video.
video = Filter(lambda m: m.video is not None, "video")

#: Match messages that carry a caption.
caption = Filter(lambda m: m.caption is not None, "caption")

#: Match messages that contain an animation.
animation = Filter(lambda m: m.animation is not None, "animation")

#: Match messages that contain a voice note.
voice = Filter(lambda m: m.voice is not None, "voice")

#: Match messages that contain a video note.
video_note = Filter(lambda m: m.video_note is not None, "video_note")

#: Match messages that contain a sticker.
sticker = Filter(lambda m: m.sticker is not None, "sticker")

#: Match messages that share a location.
location = Filter(lambda m: m.location is not None, "location")

#: Match messages that share a venue.
venue = Filter(lambda m: m.venue is not None, "venue")

#: Match messages that share a contact.
contact = Filter(lambda m: m.contact is not None, "contact")

#: Match messages that contain a poll.
poll = Filter(lambda m: m.poll is not None, "poll")

#: Match messages that contain a dice throw.
dice = Filter(lambda m: m.dice is not None, "dice")
