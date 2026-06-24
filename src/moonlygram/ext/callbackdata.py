"""Arbitrary callback data.

Telegram limits an inline button's callback_data to 64 bytes of text. This cache
lifts that limit: when a button carries a non-string callback_data, the outgoing
keyboard is rewritten to send a short opaque token instead, and the original
object is remembered. When the user taps the button, the incoming CallbackQuery's
data is swapped back to that object before handlers see it.

The cache is a bounded LRU keyed by token. If a button's object has been evicted
by the time it is tapped (the keyboard is older than maxsize others), the token
is left in place rather than resolved. Enable this with
ApplicationBuilder.arbitrary_callback_data(...).
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Any
from uuid import uuid4

from ..types import InlineKeyboardButton, InlineKeyboardMarkup

_MISSING = object()


class CallbackDataCache:
    """A bounded token-to-object store for arbitrary callback data."""

    def __init__(self, maxsize: int = 1024) -> None:
        self.maxsize = maxsize
        self._data: "OrderedDict[str, Any]" = OrderedDict()

    def put(self, obj: Any) -> str:
        """Store an object and return the token that stands in for it."""
        token = uuid4().hex
        self._data[token] = obj
        self._data.move_to_end(token)
        while len(self._data) > self.maxsize:
            self._data.popitem(last=False)
        return token

    def get(self, token: str) -> Any:
        """Return the object for a token (marking it recently used), or _MISSING."""
        if token not in self._data:
            return _MISSING
        self._data.move_to_end(token)
        return self._data[token]

    def process_keyboard(self, markup: Any) -> Any:
        """Rewrite non-string callback_data in an inline keyboard to tokens.

        Other markup types, and buttons whose callback_data is already a string,
        are returned untouched. A rewritten keyboard is a fresh object, so the
        caller's original markup is never mutated.
        """
        if not isinstance(markup, InlineKeyboardMarkup):
            return markup
        changed = False
        new_rows: list[list[InlineKeyboardButton]] = []
        for row in markup.inline_keyboard:
            new_row: list[InlineKeyboardButton] = []
            for button in row:
                data = button.callback_data
                if data is not None and not isinstance(data, str):
                    token = self.put(data)
                    new_row.append(
                        InlineKeyboardButton(
                            text=button.text, callback_data=token, url=button.url
                        )
                    )
                    changed = True
                else:
                    new_row.append(button)
            new_rows.append(new_row)
        return InlineKeyboardMarkup(new_rows) if changed else markup

    def process_callback_query(self, query: Any) -> None:
        """Swap a query's token data back to the stored object, in place."""
        data = query.data
        if isinstance(data, str):
            obj = self.get(data)
            if obj is not _MISSING:
                query.data = obj
