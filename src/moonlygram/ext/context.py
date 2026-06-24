"""The context object passed to handler callbacks."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Optional, Type

if TYPE_CHECKING:
    from ..bot import Bot
    from .jobqueue import Job, JobQueue


class CallbackContext:
    """Per-update context handed to every handler callback.

    Carries the Bot, any command arguments parsed by the handler, and three
    dictionaries for sharing state across handlers: bot_data is shared by all
    updates, while chat_data and user_data are scoped to the update's chat and
    sender. Inside an error handler, error holds the exception that was raised.
    Inside a job callback, job holds the running Job.
    """

    __slots__ = (
        "bot",
        "args",
        "bot_data",
        "chat_data",
        "user_data",
        "error",
        "job",
        "job_queue",
    )

    def __init__(
        self,
        bot: "Bot",
        *,
        args: Optional[list[str]] = None,
        bot_data: Optional[dict[Any, Any]] = None,
        chat_data: Optional[dict[Any, Any]] = None,
        user_data: Optional[dict[Any, Any]] = None,
        error: Optional[BaseException] = None,
        job: "Optional[Job]" = None,
        job_queue: "Optional[JobQueue]" = None,
    ) -> None:
        self.bot = bot
        self.args = args
        self.bot_data = bot_data if bot_data is not None else {}
        self.chat_data = chat_data if chat_data is not None else {}
        self.user_data = user_data if user_data is not None else {}
        self.error = error
        self.job = job
        self.job_queue = job_queue


class ContextTypes:
    """Pluggable types for the context object and its data dictionaries.

    Pass an instance to the builder's context_types(...) to swap in a
    CallbackContext subclass, or to make bot_data/chat_data/user_data something
    other than plain dicts (any zero-argument callable returning a mapping).
    The Application uses these factories when it creates per-update contexts and
    when it allocates the data stores.
    """

    def __init__(
        self,
        context: "Type[CallbackContext]" = CallbackContext,
        bot_data: Callable[[], Any] = dict,
        chat_data: Callable[[], Any] = dict,
        user_data: Callable[[], Any] = dict,
    ) -> None:
        self.context = context
        self.bot_data = bot_data
        self.chat_data = chat_data
        self.user_data = user_data
