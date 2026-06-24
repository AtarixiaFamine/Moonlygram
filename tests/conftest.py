"""Shared test scaffolding.

Offline only: no network or token. ``FakeSession`` records the calls a Bot
method builds (so tests assert on the exact payload); ``mock_bot`` wires a real
Session to an httpx ``MockTransport`` for round-trip transport tests. The small
``_msg`` / ``_update`` builders keep update construction terse.
"""
from __future__ import annotations

from typing import Any

import httpx

from moonlygram import Bot, Message
from moonlygram.session import Session, _serialize
from moonlygram.types import Chat, Update, User


class FakeSession:
    """Stand-in for Session: records calls and returns a canned result.

    Mirrors Session by dropping parameters set to None, so tests can assert on
    the exact payload a Bot method builds.
    """

    def __init__(self, result: Any = None) -> None:
        self.result = result
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def call(self, method: str, /, **params: Any) -> Any:
        self.calls.append(
            (method, {k: _serialize(v) for k, v in params.items() if v is not None})
        )
        return self.result

    async def close(self) -> None:
        pass


def fake_bot(result: Any = None) -> tuple[Bot, FakeSession]:
    """Build a Bot wired to a FakeSession, without opening an HTTP client."""
    bot = object.__new__(Bot)
    session = FakeSession(result)
    bot.session = session  # type: ignore[attr-defined]
    bot.defaults = None  # type: ignore[attr-defined]
    bot.rate_limiter = None  # type: ignore[attr-defined]
    bot.callback_data_cache = None  # type: ignore[attr-defined]
    return bot, session


def mock_bot(handler: Any) -> Bot:
    """Build a Bot whose Session talks to an httpx MockTransport handler."""
    session = object.__new__(Session)
    session._token = "T"  # type: ignore[attr-defined]
    session._base = "https://api.telegram.org/botT"  # type: ignore[attr-defined]
    session._file_base = "https://api.telegram.org/file/botT"  # type: ignore[attr-defined]
    session._http = httpx.AsyncClient(transport=httpx.MockTransport(handler))  # type: ignore[attr-defined]
    bot = object.__new__(Bot)
    bot.session = session  # type: ignore[attr-defined]
    bot.defaults = None  # type: ignore[attr-defined]
    bot.rate_limiter = None  # type: ignore[attr-defined]
    bot.callback_data_cache = None  # type: ignore[attr-defined]
    return bot


def _msg(text: str | None = None, *, chat_type: str = "private", from_id: int | None = None) -> Message:
    from_user = User(id=from_id, is_bot=False, first_name="T") if from_id else None
    return Message(message_id=1, chat=Chat(id=1, type=chat_type), from_user=from_user, text=text)


def _update(message: Message) -> Update:
    return Update(update_id=1, message=message)


def _conv_update(text: str, *, from_id: int = 1, update_id: int = 1) -> Update:
    return Update(update_id=update_id, message=_msg(text, from_id=from_id))


_MESSAGE_DICT = {"message_id": 10, "chat": {"id": 1, "type": "private"}, "text": "x"}

_POLL_RAW = {
    "id": "p",
    "question": "Q?",
    "options": [{"text": "x", "voter_count": 0}],
    "total_voter_count": 0,
    "is_closed": False,
    "is_anonymous": True,
    "type": "regular",
    "allows_multiple_answers": False,
}

# Conversation states shared by the ConversationHandler and persistence tests.
ASK_NAME, ASK_AGE = 1, 2

_FULL_MESSAGE_RAW = {
    "message_id": 42,
    "date": 1000,
    "edit_date": 1001,
    "message_thread_id": 7,
    "chat": {"id": 100, "type": "supergroup"},
    "from": {"id": 5, "is_bot": False, "first_name": "A"},
    "via_bot": {"id": 9, "is_bot": True, "first_name": "Bot"},
    "author_signature": "Admin",
    "has_protected_content": True,
    "is_automatic_forward": True,
    "text": "hello",
    "reply_to_message": {
        "message_id": 41,
        "chat": {"id": 200, "type": "private"},
        "text": "original",
    },
    "new_chat_members": [
        {"id": 11, "is_bot": False, "first_name": "New1"},
        {"id": 12, "is_bot": False, "first_name": "New2"},
    ],
    "left_chat_member": {"id": 13, "is_bot": False, "first_name": "Gone"},
    "pinned_message": {
        "message_id": 40,
        "chat": {"id": 100, "type": "supergroup"},
        "text": "pinned",
    },
}
