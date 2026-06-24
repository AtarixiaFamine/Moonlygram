"""Update handlers.

A handler pairs a predicate (check_update) with an async callback. The
Application checks each registered handler against an incoming update and runs
the callbacks of those that match. Callbacks take (update, context).
"""
from __future__ import annotations

import asyncio
import re
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional

from ..types import Update
from .filters import Predicate

if TYPE_CHECKING:
    from .context import CallbackContext

Callback = Callable[[Update, "CallbackContext"], Awaitable[Any]]


class BaseHandler:
    """Base class for handlers: a callback plus a check_update predicate.

    block controls dispatch when the Application processes updates
    concurrently: a blocking handler is awaited inline, so later groups wait
    for it; a non-blocking one is scheduled as a background task.
    """

    def __init__(self, callback: Callback, *, block: bool = True) -> None:
        self.callback = callback
        self.block = block

    def check_update(self, update: Update) -> bool:
        """Return whether this handler should run for the update."""
        raise NotImplementedError

    def collect_args(self, update: Update) -> Optional[list[str]]:
        """Command arguments to expose on the context, or None if not applicable."""
        return None

    async def handle(self, update: Update, context: "CallbackContext") -> Any:
        """Run the callback and return its value. Override to compose handlers."""
        return await self.callback(update, context)


class CommandHandler(BaseHandler):
    """Run the callback when a message starts with /name or /name@botusername.

    Pass a single command name or a list of names; context.args holds the
    whitespace-separated tokens that follow the command.
    """

    def __init__(
        self, command: str | list[str], callback: Callback, *, block: bool = True
    ) -> None:
        super().__init__(callback, block=block)
        self.commands = {command} if isinstance(command, str) else set(command)

    def check_update(self, update: Update) -> bool:
        message = update.effective_message
        if message is None or not message.text:
            return False
        first = message.text.split(maxsplit=1)[0]
        if not first.startswith("/"):
            return False
        return first[1:].split("@", 1)[0] in self.commands

    def collect_args(self, update: Update) -> Optional[list[str]]:
        message = update.effective_message
        if message is None or not message.text:
            return []
        return message.text.split()[1:]


class MessageHandler(BaseHandler):
    """Run the callback when a message passes the given filter."""

    def __init__(
        self, filters: Predicate, callback: Callback, *, block: bool = True
    ) -> None:
        super().__init__(callback, block=block)
        self.filters = filters

    def check_update(self, update: Update) -> bool:
        message = update.effective_message
        return message is not None and bool(self.filters(message))


class PrefixHandler(BaseHandler):
    """Run the callback when a message starts with a prefix plus command, e.g. !help.

    Pass one or more prefixes and command names; context.args holds the tokens
    after the command.
    """

    def __init__(
        self,
        prefix: str | list[str],
        command: str | list[str],
        callback: Callback,
        *,
        block: bool = True,
    ) -> None:
        super().__init__(callback, block=block)
        self.prefixes = [prefix] if isinstance(prefix, str) else list(prefix)
        self.commands = {command} if isinstance(command, str) else set(command)

    def check_update(self, update: Update) -> bool:
        message = update.effective_message
        if message is None or not message.text:
            return False
        first = message.text.split(maxsplit=1)[0]
        for prefix in self.prefixes:
            if first.startswith(prefix):
                return first[len(prefix):] in self.commands
        return False

    def collect_args(self, update: Update) -> Optional[list[str]]:
        message = update.effective_message
        if message is None or not message.text:
            return []
        return message.text.split()[1:]


class TypeHandler(BaseHandler):
    """Run the callback for every update, optionally narrowed by a predicate."""

    def __init__(
        self,
        callback: Callback,
        *,
        predicate: Optional[Callable[[Update], bool]] = None,
        block: bool = True,
    ) -> None:
        super().__init__(callback, block=block)
        self.predicate = predicate

    def check_update(self, update: Update) -> bool:
        return self.predicate is None or bool(self.predicate(update))


class CallbackQueryHandler(BaseHandler):
    """Run the callback on a callback query, optionally filtered by its data.

    If pattern is given, the query's data must match it (re.search).
    """

    def __init__(
        self,
        callback: Callback,
        *,
        pattern: str | re.Pattern[str] | None = None,
        block: bool = True,
    ) -> None:
        super().__init__(callback, block=block)
        self.pattern = re.compile(pattern) if pattern is not None else None

    def check_update(self, update: Update) -> bool:
        query = update.callback_query
        if query is None:
            return False
        if self.pattern is None:
            return True
        return query.data is not None and self.pattern.search(query.data) is not None


class ConversationHandler(BaseHandler):
    """A per-conversation state machine layered over other handlers.

    entry_points start a conversation; afterwards the update is routed to the
    handlers registered for the current state. A child callback's return value
    drives the transition: a state value moves there, ConversationHandler.END
    ends the conversation, and None keeps the current state. Conversations are
    keyed by (chat_id, user_id) by default; per_chat / per_user drop a dimension
    and per_message adds the message the update concerns (for keyboard-only
    flows).

    conversation_timeout ends a conversation after that many seconds of
    inactivity, using a lightweight asyncio timer (no JobQueue dependency).
    When nested inside another ConversationHandler, map_to_parent maps a child
    return value to a parent state, ending the child and handing control back.
    """

    END = -1

    def __init__(
        self,
        entry_points: list[BaseHandler],
        states: dict[Any, list[BaseHandler]],
        fallbacks: Optional[list[BaseHandler]] = None,
        *,
        per_chat: bool = True,
        per_user: bool = True,
        per_message: bool = False,
        allow_reentry: bool = False,
        conversation_timeout: Optional[float] = None,
        map_to_parent: Optional[dict[Any, Any]] = None,
        name: Optional[str] = None,
        persistent: bool = False,
    ) -> None:
        # ConversationHandler has no single callback; it delegates to children.
        self.callback = None  # type: ignore[assignment]
        self.block = True
        self.entry_points = entry_points
        self.states = states
        self.fallbacks = fallbacks or []
        self.per_chat = per_chat
        self.per_user = per_user
        self.per_message = per_message
        self.allow_reentry = allow_reentry
        self.conversation_timeout = conversation_timeout
        self.map_to_parent = map_to_parent
        self.name = name
        self.persistent = persistent
        self._conversations: dict[tuple[Any, ...], Any] = {}
        self._timeout_tasks: dict[tuple[Any, ...], asyncio.Task[None]] = {}

    def _message_id(self, update: Update) -> Optional[int]:
        query = update.callback_query
        if query is not None and query.message is not None:
            return query.message.message_id
        message = update.effective_message
        return message.message_id if message is not None else None

    def _key(self, update: Update) -> tuple[Any, ...]:
        parts: list[Any] = []
        if self.per_chat:
            parts.append(update.effective_chat_id)
        if self.per_user:
            parts.append(update.effective_user_id)
        if self.per_message:
            parts.append(self._message_id(update))
        return tuple(parts)

    def _candidates(self, state: Any) -> list[BaseHandler]:
        if state is None:
            return list(self.entry_points)
        candidates = list(self.states.get(state, []))
        if self.allow_reentry:
            candidates.extend(self.entry_points)
        candidates.extend(self.fallbacks)
        return candidates

    def _resolve(
        self, update: Update
    ) -> Optional[tuple[tuple[Any, ...], BaseHandler]]:
        key = self._key(update)
        state = self._conversations.get(key)
        for handler in self._candidates(state):
            if handler.check_update(update):
                return key, handler
        return None

    def check_update(self, update: Update) -> bool:
        return self._resolve(update) is not None

    async def handle(self, update: Update, context: "CallbackContext") -> Any:
        resolved = self._resolve(update)
        if resolved is None:
            return None
        key, handler = resolved
        context.args = handler.collect_args(update)
        new_state = await handler.handle(update, context)

        if (
            new_state is not None
            and self.map_to_parent is not None
            and new_state in self.map_to_parent
        ):
            # Nested: end this conversation and bubble the mapped state upward.
            self._end(key)
            return self.map_to_parent[new_state]

        self._transition(key, new_state)
        return None

    def _transition(self, key: tuple[Any, ...], new_state: Any) -> None:
        if new_state is None:
            # Stay in the current state; refresh the inactivity timer.
            if key in self._conversations:
                self._schedule_timeout(key)
        elif new_state == self.END:
            self._end(key)
        else:
            self._conversations[key] = new_state
            self._schedule_timeout(key)

    def _end(self, key: tuple[Any, ...]) -> None:
        self._conversations.pop(key, None)
        self._cancel_timeout(key)

    def _schedule_timeout(self, key: tuple[Any, ...]) -> None:
        if self.conversation_timeout is None:
            return
        self._cancel_timeout(key)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        self._timeout_tasks[key] = loop.create_task(self._run_timeout(key))

    def _cancel_timeout(self, key: tuple[Any, ...]) -> None:
        task = self._timeout_tasks.pop(key, None)
        if task is not None:
            task.cancel()

    async def _run_timeout(self, key: tuple[Any, ...]) -> None:
        try:
            await asyncio.sleep(self.conversation_timeout)  # type: ignore[arg-type]
        except asyncio.CancelledError:
            return
        self._conversations.pop(key, None)
        self._timeout_tasks.pop(key, None)


class ChatMemberHandler(BaseHandler):
    """Run the callback on chat member updates.

    By default it matches both my_chat_member (the bot's own status changes) and
    chat_member (other members); pass kind to narrow it.
    """

    MY_CHAT_MEMBER = "my_chat_member"
    CHAT_MEMBER = "chat_member"
    ANY = "any"

    def __init__(
        self, callback: Callback, *, kind: str = "any", block: bool = True
    ) -> None:
        super().__init__(callback, block=block)
        self.kind = kind

    def check_update(self, update: Update) -> bool:
        if self.kind == self.MY_CHAT_MEMBER:
            return update.my_chat_member is not None
        if self.kind == self.CHAT_MEMBER:
            return update.chat_member is not None
        return update.my_chat_member is not None or update.chat_member is not None


class ChatJoinRequestHandler(BaseHandler):
    """Run the callback on chat join requests (the chat_join_request update)."""

    def check_update(self, update: Update) -> bool:
        return update.chat_join_request is not None


class InlineQueryHandler(BaseHandler):
    """Run the callback on an inline query, optionally filtered by its text.

    If pattern is given, the query text must match it (re.search).
    """

    def __init__(
        self,
        callback: Callback,
        *,
        pattern: str | re.Pattern[str] | None = None,
        block: bool = True,
    ) -> None:
        super().__init__(callback, block=block)
        self.pattern = re.compile(pattern) if pattern is not None else None

    def check_update(self, update: Update) -> bool:
        query = update.inline_query
        if query is None:
            return False
        if self.pattern is None:
            return True
        return self.pattern.search(query.query) is not None


class ChosenInlineResultHandler(BaseHandler):
    """Run the callback when the user chooses an inline query result."""

    def check_update(self, update: Update) -> bool:
        return update.chosen_inline_result is not None


class PollHandler(BaseHandler):
    """Run the callback on poll state updates (the poll update).

    Telegram sends these when a poll the bot created is voted on or stopped.
    """

    def check_update(self, update: Update) -> bool:
        return update.poll is not None


class PollAnswerHandler(BaseHandler):
    """Run the callback when a user changes their vote in a non-anonymous poll."""

    def check_update(self, update: Update) -> bool:
        return update.poll_answer is not None


class MessageReactionHandler(BaseHandler):
    """Run the callback on message reaction updates.

    By default it matches both message_reaction (a single user's reaction
    change, when the bot can see it) and message_reaction_count (anonymous
    totals); pass kind to narrow it.
    """

    MESSAGE_REACTION = "message_reaction"
    MESSAGE_REACTION_COUNT = "message_reaction_count"
    ANY = "any"

    def __init__(
        self, callback: Callback, *, kind: str = "any", block: bool = True
    ) -> None:
        super().__init__(callback, block=block)
        self.kind = kind

    def check_update(self, update: Update) -> bool:
        if self.kind == self.MESSAGE_REACTION:
            return update.message_reaction is not None
        if self.kind == self.MESSAGE_REACTION_COUNT:
            return update.message_reaction_count is not None
        return (
            update.message_reaction is not None
            or update.message_reaction_count is not None
        )


class ChatBoostHandler(BaseHandler):
    """Run the callback on chat boost updates.

    By default it matches both chat_boost (a boost added or changed) and
    removed_chat_boost (a boost removed); pass kind to narrow it.
    """

    CHAT_BOOST = "chat_boost"
    REMOVED_CHAT_BOOST = "removed_chat_boost"
    ANY = "any"

    def __init__(
        self, callback: Callback, *, kind: str = "any", block: bool = True
    ) -> None:
        super().__init__(callback, block=block)
        self.kind = kind

    def check_update(self, update: Update) -> bool:
        if self.kind == self.CHAT_BOOST:
            return update.chat_boost is not None
        if self.kind == self.REMOVED_CHAT_BOOST:
            return update.removed_chat_boost is not None
        return update.chat_boost is not None or update.removed_chat_boost is not None
