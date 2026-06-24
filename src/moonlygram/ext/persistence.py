"""Persistence backends for Application state.

A persistence object loads bot/chat/user data and conversation states on
Application.initialize() and is flushed on shutdown() (or an explicit
Application.update_persistence()). State is snapshot-based: it survives a clean
shutdown, not a hard crash mid-run.
"""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, cast

ChatData = dict[int, dict[Any, Any]]
Conversations = dict[str, dict[tuple[Any, ...], Any]]


class BasePersistence:
    """Interface for loading and flushing Application state."""

    async def load_bot_data(self) -> dict[Any, Any]:
        raise NotImplementedError

    async def load_chat_data(self) -> ChatData:
        raise NotImplementedError

    async def load_user_data(self) -> ChatData:
        raise NotImplementedError

    async def load_conversations(self, name: str) -> dict[tuple[Any, ...], Any]:
        raise NotImplementedError

    async def flush(
        self,
        *,
        bot_data: dict[Any, Any],
        chat_data: ChatData,
        user_data: ChatData,
        conversations: Conversations,
    ) -> None:
        raise NotImplementedError


class DictPersistence(BasePersistence):
    """In-memory persistence holding the last flushed snapshot.

    Handy for tests and for handing state to another store. Loaded data is
    copied so callers cannot mutate the stored snapshot in place.
    """

    def __init__(
        self,
        *,
        bot_data: dict[Any, Any] | None = None,
        chat_data: ChatData | None = None,
        user_data: ChatData | None = None,
        conversations: Conversations | None = None,
    ) -> None:
        self.bot_data = bot_data or {}
        self.chat_data = chat_data or {}
        self.user_data = user_data or {}
        self.conversations = conversations or {}

    async def load_bot_data(self) -> dict[Any, Any]:
        return dict(self.bot_data)

    async def load_chat_data(self) -> ChatData:
        return {key: dict(value) for key, value in self.chat_data.items()}

    async def load_user_data(self) -> ChatData:
        return {key: dict(value) for key, value in self.user_data.items()}

    async def load_conversations(self, name: str) -> dict[tuple[Any, ...], Any]:
        return dict(self.conversations.get(name, {}))

    async def flush(
        self,
        *,
        bot_data: dict[Any, Any],
        chat_data: ChatData,
        user_data: ChatData,
        conversations: Conversations,
    ) -> None:
        self.bot_data = bot_data
        self.chat_data = chat_data
        self.user_data = user_data
        self.conversations = conversations


class PicklePersistence(BasePersistence):
    """File-backed persistence using a single pickle file."""

    def __init__(self, filepath: str) -> None:
        self.filepath = Path(filepath)

    def _read(self) -> dict[str, Any]:
        if not self.filepath.exists():
            return {}
        with self.filepath.open("rb") as handle:
            return cast("dict[str, Any]", pickle.load(handle))

    async def load_bot_data(self) -> dict[Any, Any]:
        return cast("dict[Any, Any]", self._read().get("bot_data", {}))

    async def load_chat_data(self) -> ChatData:
        return cast(ChatData, self._read().get("chat_data", {}))

    async def load_user_data(self) -> ChatData:
        return cast(ChatData, self._read().get("user_data", {}))

    async def load_conversations(self, name: str) -> dict[tuple[Any, ...], Any]:
        return cast(
            "dict[tuple[Any, ...], Any]",
            self._read().get("conversations", {}).get(name, {}),
        )

    async def flush(
        self,
        *,
        bot_data: dict[Any, Any],
        chat_data: ChatData,
        user_data: ChatData,
        conversations: Conversations,
    ) -> None:
        data = {
            "bot_data": bot_data,
            "chat_data": chat_data,
            "user_data": user_data,
            "conversations": conversations,
        }
        with self.filepath.open("wb") as handle:
            pickle.dump(data, handle)
