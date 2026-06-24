"""The Application: handler registry, update dispatch, and polling loop.

Application owns a Bot, holds the registered handlers, and runs the update
loop that feeds incoming updates to them. Build one with
Application.builder().token(...).build().

Entry points come in sync and async pairs:

- run_polling() / run_webhook() are synchronous and blocking; each owns the
  event loop and shuts down cleanly on SIGINT/SIGTERM. Use one for a standalone
  bot.
- start_polling() / start_webhook() are the async primitives (await them, or
  gather with other tasks). Pair with initialize()/shutdown(), or ``async with
  app``. feed_webhook_update() dispatches a single update from your own server.

In every mode, receiving and dispatch run concurrently through an internal
queue, so a slow handler never delays the next update.
"""
from __future__ import annotations

import asyncio
import json
import logging
import signal
from collections import defaultdict
from typing import Any, Awaitable, Callable, Optional

from ..bot import Bot
from ..defaults import Defaults
from ..errors import APIError, FloodWait, NetworkError, Unauthorized
from ..types import Update, User
from .callbackdata import CallbackDataCache
from .context import CallbackContext, ContextTypes
from .handlers import BaseHandler, Callback, ConversationHandler
from .jobqueue import JobQueue
from .persistence import BasePersistence

logger = logging.getLogger("moonlygram")

_UNSET = object()

# A lifecycle hook receives the running Application and returns nothing useful.
LifecycleHook = Callable[["Application"], Awaitable[Any]]


class ApplicationHandlerStop(Exception):
    """Raise from a handler callback to stop all further handler processing."""


class Application:
    def __init__(
        self,
        bot: Bot,
        *,
        poll_timeout: int = 10,
        allowed_updates: Optional[list[str]] = None,
        persistence: Optional[BasePersistence] = None,
        job_queue: Optional[JobQueue] = None,
        concurrent_updates: bool | int = False,
        context_types: Optional[ContextTypes] = None,
        post_init: Optional[LifecycleHook] = None,
        post_stop: Optional[LifecycleHook] = None,
        post_shutdown: Optional[LifecycleHook] = None,
    ) -> None:
        self.bot = bot
        self.bot_user: Optional[User] = None
        self.persistence = persistence
        self.job_queue = job_queue
        self.context_types = context_types or ContextTypes()
        self.post_init = post_init
        self.post_stop = post_stop
        self.post_shutdown = post_shutdown
        if job_queue is not None:
            job_queue.set_application(self)
        self._concurrent_updates = (
            256 if concurrent_updates is True else int(concurrent_updates or 0)
        )
        self._background_tasks: set[asyncio.Task[None]] = set()
        self.handlers: dict[int, list[BaseHandler]] = {}
        self.error_handlers: list[Callback] = []
        self.bot_data: Any = self.context_types.bot_data()
        self._chat_data: dict[int, Any] = defaultdict(self.context_types.chat_data)
        self._user_data: dict[int, Any] = defaultdict(self.context_types.user_data)
        self._poll_timeout = poll_timeout
        self._allowed_updates = allowed_updates
        self._backoff_base = 1.0
        self._backoff_max = 30.0
        self._running = False
        self._stop_event: Optional[asyncio.Event] = None
        self._webhook_server: Optional[asyncio.AbstractServer] = None

    @staticmethod
    def builder() -> "ApplicationBuilder":
        """Return a builder for the Application.builder().token(...).build() idiom."""
        return ApplicationBuilder()

    async def __aenter__(self) -> "Application":
        await self.initialize()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.shutdown()

    def add_handler(self, handler: BaseHandler, group: int = 0) -> None:
        """Register a handler in a group.

        Groups run in ascending order; within a group only the first matching
        handler runs.
        """
        self.handlers.setdefault(group, []).append(handler)

    def add_error_handler(self, callback: Callback) -> None:
        """Register a callback to handle exceptions raised during dispatch.

        The callback receives (update, context) with the offending exception on
        context.error. Several may be registered; all run. With none registered
        the error is logged and processing continues, as before.
        """
        self.error_handlers.append(callback)

    async def _dispatch_error(
        self,
        update: Optional[Update],
        context: Optional[CallbackContext],
        error: Exception,
    ) -> None:
        """Send an exception to the error handlers, or log it if there are none."""
        if not self.error_handlers:
            logger.error("Unhandled error in handler", exc_info=error)
            return
        if context is None:
            context = (
                self._build_context(update, None)
                if update is not None
                else self.context_types.context(self.bot, bot_data=self.bot_data)
            )
        context.error = error
        for callback in self.error_handlers:
            try:
                # update is None for errors raised outside an update (e.g. a job).
                await callback(update, context)  # type: ignore[arg-type]
            except Exception:
                logger.exception("Error raised inside an error handler")

    async def initialize(self) -> None:
        """Confirm the token, cache the bot's own user, and load persisted state.

        Fails fast on a bad token.
        """
        self.bot_user = await self.bot.get_me()
        logger.info("Moonlygram initialized as @%s", self.bot_user.username)
        if self.bot.rate_limiter is not None:
            await self.bot.rate_limiter.initialize()
        if self.persistence is not None:
            self.bot_data = await self.persistence.load_bot_data()
            self._chat_data = defaultdict(
                self.context_types.chat_data, await self.persistence.load_chat_data()
            )
            self._user_data = defaultdict(
                self.context_types.user_data, await self.persistence.load_user_data()
            )
            for name, handler in self._persistent_conversations().items():
                handler._conversations = await self.persistence.load_conversations(name)
        if self.job_queue is not None:
            self.job_queue.start()

    async def shutdown(self) -> None:
        """Stop jobs, flush persisted state (if any), and close the HTTP session."""
        if self.job_queue is not None:
            await self.job_queue.stop()
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        if self.persistence is not None:
            await self.update_persistence()
        if self.bot.rate_limiter is not None:
            await self.bot.rate_limiter.shutdown()
        await self.bot.close()

    def _persistent_conversations(self) -> dict[str, ConversationHandler]:
        result: dict[str, ConversationHandler] = {}
        for group in self.handlers.values():
            for handler in group:
                if (
                    isinstance(handler, ConversationHandler)
                    and handler.persistent
                    and handler.name is not None
                ):
                    result[handler.name] = handler
        return result

    async def update_persistence(self) -> None:
        """Flush bot/chat/user data and conversation state to persistence."""
        if self.persistence is None:
            return
        conversations = {
            name: dict(handler._conversations)
            for name, handler in self._persistent_conversations().items()
        }
        await self.persistence.flush(
            bot_data=self.bot_data,
            chat_data={k: dict(v) for k, v in self._chat_data.items()},
            user_data={k: dict(v) for k, v in self._user_data.items()},
            conversations=conversations,
        )

    def _build_context(
        self, update: Update, args: Optional[list[str]]
    ) -> CallbackContext:
        chat_id = update.effective_chat_id
        user_id = update.effective_user_id
        return self.context_types.context(
            self.bot,
            args=args,
            bot_data=self.bot_data,
            chat_data=self._chat_data[chat_id] if chat_id is not None else {},
            user_data=self._user_data[user_id] if user_id is not None else {},
            job_queue=self.job_queue,
        )

    async def process_update(self, update: Update) -> None:
        """Dispatch one update through the handler groups.

        Groups run in ascending order; within a group the first matching handler
        runs and the rest of that group is skipped. A handler may raise
        ApplicationHandlerStop to halt all processing; other exceptions are sent
        to the registered error handlers (or logged) and do not stop the
        remaining groups. A non-blocking handler (block=False) is run as a
        background task so later groups are not delayed by it; it cannot halt
        processing.
        """
        try:
            update.set_bot(self.bot)
        except Exception as exc:
            await self._dispatch_error(update, None, exc)
            return
        if update.callback_query is not None and self.bot.callback_data_cache is not None:
            self.bot.callback_data_cache.process_callback_query(update.callback_query)
        for group in sorted(self.handlers):
            for handler in self.handlers[group]:
                if not handler.check_update(update):
                    continue
                context = self._build_context(update, handler.collect_args(update))
                if not handler.block:
                    self._run_in_background(handler, update, context)
                    break
                try:
                    await handler.handle(update, context)
                except ApplicationHandlerStop:
                    return
                except Exception as exc:
                    await self._dispatch_error(update, context, exc)
                break

    def _run_in_background(
        self, handler: BaseHandler, update: Update, context: CallbackContext
    ) -> None:
        task = asyncio.ensure_future(self._background_handler(handler, update, context))
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    async def _background_handler(
        self, handler: BaseHandler, update: Update, context: CallbackContext
    ) -> None:
        try:
            await handler.handle(update, context)
        except ApplicationHandlerStop:
            pass  # a detached handler cannot halt the other groups
        except Exception as exc:
            await self._dispatch_error(update, context, exc)

    async def start_polling(self) -> None:
        """Poll getUpdates and dispatch updates until stop() is called.

        This is the async primitive; await it directly or gather it with other
        coroutines. It does not initialize or shut down the bot.
        """
        self._running = True
        self._stop_event = asyncio.Event()
        queue: asyncio.Queue[Optional[Update]] = asyncio.Queue()
        try:
            await asyncio.gather(self._produce(queue), self._consume(queue))
        finally:
            self._running = False
            self._stop_event = None

    async def _produce(self, queue: asyncio.Queue[Optional[Update]]) -> None:
        assert self._stop_event is not None
        offset: Optional[int] = None
        failures = 0
        try:
            while not self._stop_event.is_set():
                poll = asyncio.ensure_future(
                    self.bot.session.call(
                        "getUpdates",
                        offset=offset,
                        timeout=self._poll_timeout,
                        allowed_updates=self._allowed_updates,
                    )
                )
                stop = asyncio.ensure_future(self._stop_event.wait())
                done, pending = await asyncio.wait(
                    {poll, stop}, return_when=asyncio.FIRST_COMPLETED
                )
                for task in pending:
                    task.cancel()
                await asyncio.gather(*pending, return_exceptions=True)
                if stop in done:
                    break
                try:
                    updates = poll.result()
                except Unauthorized:
                    raise  # a bad token will not fix itself
                except FloodWait as flood:
                    await asyncio.sleep(flood.retry_after)
                    continue
                except (APIError, NetworkError) as exc:
                    failures += 1
                    delay = min(self._backoff_base * 2 ** (failures - 1), self._backoff_max)
                    logger.warning("getUpdates failed (%s); retrying in %.1fs", exc, delay)
                    await asyncio.sleep(delay)
                    continue
                failures = 0
                for raw in updates:
                    update = Update.from_dict(raw)
                    offset = update.update_id + 1
                    await queue.put(update)
        finally:
            await queue.put(None)

    async def _consume(self, queue: asyncio.Queue[Optional[Update]]) -> None:
        if not self._concurrent_updates:
            while True:
                update = await queue.get()
                if update is None:
                    return
                await self.process_update(update)
            return
        # Process up to _concurrent_updates updates at once; the semaphore both
        # caps concurrency and applies backpressure on the queue.
        semaphore = asyncio.Semaphore(self._concurrent_updates)
        tasks: set[asyncio.Task[None]] = set()
        while True:
            update = await queue.get()
            if update is None:
                break
            await semaphore.acquire()
            task = asyncio.ensure_future(self._process_guarded(update, semaphore))
            tasks.add(task)
            task.add_done_callback(tasks.discard)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_guarded(
        self, update: Update, semaphore: asyncio.Semaphore
    ) -> None:
        try:
            await self.process_update(update)
        finally:
            semaphore.release()

    def run_polling(self) -> None:
        """Run the bot until interrupted. Blocking; owns and closes the event loop."""
        try:
            asyncio.run(self._run_polling())
        except KeyboardInterrupt:
            pass

    async def _run_polling(self) -> None:
        self._install_signal_handlers(asyncio.get_running_loop())
        await self.initialize()
        if self.post_init is not None:
            await self.post_init(self)
        try:
            await self.start_polling()
        finally:
            if self.post_stop is not None:
                await self.post_stop(self)
            await self.shutdown()
            if self.post_shutdown is not None:
                await self.post_shutdown(self)

    async def feed_webhook_update(self, data: dict[str, Any] | Update) -> None:
        """Parse a raw webhook update (or an Update) and dispatch it.

        Use this to wire Moonlygram into your own web framework instead of the
        built-in webhook server.
        """
        update = data if isinstance(data, Update) else Update.from_dict(data)
        await self.process_update(update)

    def run_webhook(
        self,
        *,
        listen: str = "127.0.0.1",
        port: int = 8443,
        url_path: str = "",
        secret_token: Optional[str] = None,
        webhook_url: Optional[str] = None,
        allowed_updates: Optional[list[str]] = None,
    ) -> None:
        """Run a webhook server until interrupted. Blocking; owns the event loop."""
        try:
            asyncio.run(
                self._run_webhook(
                    listen=listen,
                    port=port,
                    url_path=url_path,
                    secret_token=secret_token,
                    webhook_url=webhook_url,
                    allowed_updates=allowed_updates,
                )
            )
        except KeyboardInterrupt:
            pass

    async def _run_webhook(self, **kwargs: Any) -> None:
        self._install_signal_handlers(asyncio.get_running_loop())
        await self.initialize()
        if self.post_init is not None:
            await self.post_init(self)
        try:
            await self.start_webhook(**kwargs)
        finally:
            if self.post_stop is not None:
                await self.post_stop(self)
            await self.shutdown()
            if self.post_shutdown is not None:
                await self.post_shutdown(self)

    async def start_webhook(
        self,
        *,
        listen: str = "127.0.0.1",
        port: int = 8443,
        url_path: str = "",
        secret_token: Optional[str] = None,
        webhook_url: Optional[str] = None,
        allowed_updates: Optional[list[str]] = None,
    ) -> None:
        """Serve updates over a webhook until stop() is called.

        A minimal HTTP server accepts Telegram's POSTs, validates the request
        path and optional secret token, and dispatches updates concurrently. If
        webhook_url is given, setWebhook is called first. This is the async
        primitive; it does not initialize or shut down the bot.
        """
        self._running = True
        self._stop_event = asyncio.Event()
        if webhook_url is not None:
            await self.bot.set_webhook(
                webhook_url, secret_token=secret_token, allowed_updates=allowed_updates
            )
        path = "/" + url_path.lstrip("/")
        queue: asyncio.Queue[Optional[Update]] = asyncio.Queue()
        consumer = asyncio.ensure_future(self._consume(queue))

        async def handle(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            await self._handle_webhook_request(reader, writer, path, secret_token, queue)

        server = await asyncio.start_server(handle, listen, port)
        self._webhook_server = server
        try:
            await self._stop_event.wait()
        finally:
            server.close()
            await server.wait_closed()
            await queue.put(None)
            await consumer
            self._webhook_server = None
            self._running = False
            self._stop_event = None

    async def _handle_webhook_request(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        path: str,
        secret_token: Optional[str],
        queue: asyncio.Queue[Optional[Update]],
    ) -> None:
        try:
            request_line = await reader.readline()
            if not request_line:
                return
            parts = request_line.decode("latin-1").split()
            if len(parts) < 2:
                await self._respond(writer, 400)
                return
            method, target = parts[0], parts[1]
            headers: dict[str, str] = {}
            while True:
                line = await reader.readline()
                if line in (b"\r\n", b"\n", b""):
                    break
                key, _, value = line.decode("latin-1").partition(":")
                headers[key.strip().lower()] = value.strip()
            length = int(headers.get("content-length", "0") or "0")
            body = await reader.readexactly(length) if length else b""

            if method != "POST" or target != path:
                await self._respond(writer, 404)
                return
            if secret_token is not None and (
                headers.get("x-telegram-bot-api-secret-token") != secret_token
            ):
                await self._respond(writer, 403)
                return
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                await self._respond(writer, 400)
                return
            await queue.put(Update.from_dict(data))
            await self._respond(writer, 200)
        except (asyncio.IncompleteReadError, ConnectionError):
            pass
        finally:
            writer.close()

    @staticmethod
    async def _respond(writer: asyncio.StreamWriter, status: int) -> None:
        reasons = {200: "OK", 400: "Bad Request", 403: "Forbidden", 404: "Not Found"}
        head = (
            f"HTTP/1.1 {status} {reasons.get(status, 'OK')}\r\n"
            "Content-Length: 0\r\n"
            "Connection: close\r\n\r\n"
        )
        writer.write(head.encode("latin-1"))
        await writer.drain()

    def _install_signal_handlers(self, loop: asyncio.AbstractEventLoop) -> None:
        for name in ("SIGINT", "SIGTERM"):
            sig = getattr(signal, name, None)
            if sig is None:
                continue
            try:
                loop.add_signal_handler(sig, self.stop)
            except (NotImplementedError, RuntimeError):
                # Windows event loops do not support add_signal_handler;
                # Ctrl-C still surfaces as KeyboardInterrupt in run_polling.
                pass

    def stop(self) -> None:
        """Signal the polling loop to finish and unwind."""
        self._running = False
        if self._stop_event is not None:
            self._stop_event.set()


class ApplicationBuilder:
    """Fluent builder mirroring python-telegram-bot's Application.builder()."""

    def __init__(self) -> None:
        self._token: Optional[str] = None
        self._session_kwargs: dict[str, Any] = {}
        self._poll_timeout = 10
        self._allowed_updates: Optional[list[str]] = None
        self._defaults: Optional[Defaults] = None
        self._persistence: Optional[BasePersistence] = None
        self._job_queue: Any = _UNSET
        self._rate_limiter: Any = None
        self._callback_data_cache: Any = None
        self._concurrent_updates: bool | int = False
        self._context_types: Optional[ContextTypes] = None
        self._post_init: Optional[LifecycleHook] = None
        self._post_stop: Optional[LifecycleHook] = None
        self._post_shutdown: Optional[LifecycleHook] = None

    def token(self, token: str) -> "ApplicationBuilder":
        """Set the bot token."""
        self._token = token
        return self

    def base_url(self, base_url: str) -> "ApplicationBuilder":
        """Override the Bot API base URL (for a local Bot API server)."""
        self._session_kwargs["base_url"] = base_url
        return self

    def poll_timeout(self, seconds: int) -> "ApplicationBuilder":
        """Set the long-polling timeout passed to getUpdates."""
        self._poll_timeout = seconds
        return self

    def allowed_updates(self, allowed_updates: list[str]) -> "ApplicationBuilder":
        """Limit which update types Telegram sends (see the getUpdates docs)."""
        self._allowed_updates = allowed_updates
        return self

    def defaults(self, defaults: Defaults) -> "ApplicationBuilder":
        """Set default parameter values applied to outgoing Bot API calls."""
        self._defaults = defaults
        return self

    def persistence(self, persistence: BasePersistence) -> "ApplicationBuilder":
        """Set the persistence backend for bot/chat/user data and conversations."""
        self._persistence = persistence
        return self

    def job_queue(self, job_queue: Optional[JobQueue]) -> "ApplicationBuilder":
        """Set the JobQueue, or pass None to disable scheduled jobs.

        When left unset, the Application gets a default JobQueue.
        """
        self._job_queue = job_queue
        return self

    def rate_limiter(self, rate_limiter: Any) -> "ApplicationBuilder":
        """Set a BaseRateLimiter to pace outgoing Bot API calls."""
        self._rate_limiter = rate_limiter
        return self

    def arbitrary_callback_data(
        self, value: bool | int = True
    ) -> "ApplicationBuilder":
        """Enable non-string callback_data on inline buttons.

        Pass True for the default cache size, an int to set it, or False to
        disable.
        """
        if value is False:
            self._callback_data_cache = None
        else:
            maxsize = 1024 if value is True else int(value)
            self._callback_data_cache = CallbackDataCache(maxsize=maxsize)
        return self

    def concurrent_updates(self, value: bool | int) -> "ApplicationBuilder":
        """Process updates concurrently: True (a default cap), an int cap, or False."""
        self._concurrent_updates = value
        return self

    def context_types(self, context_types: ContextTypes) -> "ApplicationBuilder":
        """Set custom types for the context object and its data dictionaries."""
        self._context_types = context_types
        return self

    def post_init(self, callback: LifecycleHook) -> "ApplicationBuilder":
        """Set a coroutine run after initialize() but before the update loop starts.

        It receives the Application; use it to set bot commands, warm caches, or
        open resources. Runs only under run_polling()/run_webhook().
        """
        self._post_init = callback
        return self

    def post_stop(self, callback: LifecycleHook) -> "ApplicationBuilder":
        """Set a coroutine run after the update loop stops but before shutdown()."""
        self._post_stop = callback
        return self

    def post_shutdown(self, callback: LifecycleHook) -> "ApplicationBuilder":
        """Set a coroutine run after shutdown() completes."""
        self._post_shutdown = callback
        return self

    def build(self) -> Application:
        """Construct the Application from the configured settings."""
        if self._token is None:
            raise ValueError("A bot token is required; call .token(...) first.")
        job_queue = JobQueue() if self._job_queue is _UNSET else self._job_queue
        return Application(
            Bot(
                self._token,
                defaults=self._defaults,
                rate_limiter=self._rate_limiter,
                callback_data_cache=self._callback_data_cache,
                **self._session_kwargs,
            ),
            poll_timeout=self._poll_timeout,
            allowed_updates=self._allowed_updates,
            persistence=self._persistence,
            job_queue=job_queue,
            concurrent_updates=self._concurrent_updates,
            context_types=self._context_types,
            post_init=self._post_init,
            post_stop=self._post_stop,
            post_shutdown=self._post_shutdown,
        )
