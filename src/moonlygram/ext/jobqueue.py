"""A dependency-free asyncio job scheduler.

JobQueue schedules callbacks to run later — once, on an interval, daily, or
monthly — without pulling in APScheduler (which python-telegram-bot uses). Each
Job owns an asyncio task that sleeps until its next run. A job callback takes a
single CallbackContext, with context.job set to the running Job and
context.job_queue set to the queue.

Scheduling helpers accept plain seconds, a datetime.timedelta, or (for run_once)
an absolute datetime; run_daily / run_monthly take a datetime.time. Times are
interpreted in the machine's local timezone.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import logging
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, Union

from .context import CallbackContext

if TYPE_CHECKING:
    from .application import Application

logger = logging.getLogger("moonlygram")

JobCallback = Callable[[CallbackContext], Awaitable[Any]]
TimeSpec = Union[float, dt.timedelta, dt.datetime]

_DEFAULT = object()


class Job:
    """A scheduled callback. Inspect or cancel it via the returned handle."""

    __slots__ = (
        "callback",
        "name",
        "data",
        "chat_id",
        "user_id",
        "_task",
        "_coro_factory",
        "_removed",
    )

    def __init__(
        self,
        callback: JobCallback,
        *,
        name: Optional[str] = None,
        data: Any = None,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> None:
        self.callback = callback
        self.name = name or getattr(callback, "__name__", "job")
        self.data = data
        self.chat_id = chat_id
        self.user_id = user_id
        self._task: Optional[asyncio.Task[None]] = None
        self._coro_factory: Optional[Callable[[], Awaitable[None]]] = None
        self._removed = False

    @property
    def removed(self) -> bool:
        """Whether this job has been cancelled and will not run again."""
        return self._removed

    def schedule_removal(self) -> None:
        """Cancel the job; a running occurrence is allowed to finish."""
        self._removed = True
        if self._task is not None:
            self._task.cancel()


class JobQueue:
    """Schedules Jobs against an Application's event loop."""

    def __init__(self) -> None:
        self._application: Optional[Application] = None
        self._jobs: set[Job] = set()
        self._running = False

    def set_application(self, application: "Application") -> None:
        """Attach the Application whose bot and data the jobs see."""
        self._application = application

    @property
    def application(self) -> "Application":
        if self._application is None:
            raise RuntimeError("JobQueue is not attached to an Application.")
        return self._application

    def jobs(self) -> list[Job]:
        """Return the currently scheduled jobs."""
        return list(self._jobs)

    def get_jobs_by_name(self, name: str) -> list[Job]:
        """Return scheduled jobs with the given name."""
        return [job for job in self._jobs if job.name == name]

    def start(self) -> None:
        """Launch any jobs scheduled before the queue was running."""
        self._running = True
        for job in list(self._jobs):
            if job._task is None and not job.removed:
                self._launch(job)

    async def stop(self) -> None:
        """Cancel all jobs and wait for their tasks to unwind."""
        self._running = False
        tasks = []
        for job in list(self._jobs):
            job.schedule_removal()
            if job._task is not None:
                tasks.append(job._task)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._jobs.clear()

    def run_once(
        self,
        callback: JobCallback,
        when: TimeSpec,
        *,
        data: Any = None,
        name: Optional[str] = None,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Job:
        """Run callback once after when (seconds, timedelta, or absolute datetime)."""
        job = Job(callback, name=name, data=data, chat_id=chat_id, user_id=user_id)
        return self._register(job, lambda: self._loop_once(job, _delay_seconds(when)))

    def run_repeating(
        self,
        callback: JobCallback,
        interval: Union[float, dt.timedelta],
        *,
        first: Optional[TimeSpec] = None,
        data: Any = None,
        name: Optional[str] = None,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Job:
        """Run callback every interval, the first time after first (default interval)."""
        seconds = _to_seconds(interval)
        first_delay = _delay_seconds(first) if first is not None else seconds
        job = Job(callback, name=name, data=data, chat_id=chat_id, user_id=user_id)
        return self._register(
            job, lambda: self._loop_repeating(job, seconds, first_delay)
        )

    def run_daily(
        self,
        callback: JobCallback,
        time: dt.time,
        *,
        data: Any = None,
        name: Optional[str] = None,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Job:
        """Run callback every day at the given local time."""
        job = Job(callback, name=name, data=data, chat_id=chat_id, user_id=user_id)
        return self._register(job, lambda: self._loop_daily(job, time))

    def run_monthly(
        self,
        callback: JobCallback,
        when: dt.time,
        day: int,
        *,
        data: Any = None,
        name: Optional[str] = None,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Job:
        """Run callback on the given day of every month at the given local time.

        Months without that day (e.g. day 31 in February) are skipped.
        """
        job = Job(callback, name=name, data=data, chat_id=chat_id, user_id=user_id)
        return self._register(job, lambda: self._loop_monthly(job, when, day))

    def _register(
        self, job: Job, coro_factory: Callable[[], Awaitable[None]]
    ) -> Job:
        job._coro_factory = coro_factory
        self._jobs.add(job)
        if self._running:
            self._launch(job)
        return job

    def _launch(self, job: Job) -> None:
        assert job._coro_factory is not None
        job._task = asyncio.ensure_future(job._coro_factory())

    def _finish(self, job: Job) -> None:
        job._removed = True
        self._jobs.discard(job)

    async def _execute(self, job: Job) -> None:
        context = self._build_context(job)
        try:
            await job.callback(context)
        except Exception as exc:
            await self.application._dispatch_error(None, context, exc)

    def _build_context(self, job: Job) -> CallbackContext:
        app = self.application
        return CallbackContext(
            app.bot,
            bot_data=app.bot_data,
            chat_data=app._chat_data[job.chat_id] if job.chat_id is not None else {},
            user_data=app._user_data[job.user_id] if job.user_id is not None else {},
            job=job,
            job_queue=self,
        )

    async def _loop_once(self, job: Job, delay: float) -> None:
        try:
            if delay > 0:
                await asyncio.sleep(delay)
            if not job.removed:
                await self._execute(job)
        except asyncio.CancelledError:
            pass
        finally:
            self._finish(job)

    async def _loop_repeating(self, job: Job, interval: float, first: float) -> None:
        loop = asyncio.get_event_loop()
        next_time = loop.time() + max(0.0, first)
        try:
            while not job.removed:
                delay = next_time - loop.time()
                if delay > 0:
                    await asyncio.sleep(delay)
                if job.removed:
                    break
                await self._execute(job)
                next_time += interval
        except asyncio.CancelledError:
            pass
        finally:
            self._finish(job)

    async def _loop_daily(self, job: Job, time: dt.time) -> None:
        try:
            while not job.removed:
                await asyncio.sleep(_seconds_until_daily(time, _now()))
                if job.removed:
                    break
                await self._execute(job)
        except asyncio.CancelledError:
            pass
        finally:
            self._finish(job)

    async def _loop_monthly(self, job: Job, time: dt.time, day: int) -> None:
        try:
            while not job.removed:
                await asyncio.sleep(_seconds_until_monthly(time, day, _now()))
                if job.removed:
                    break
                await self._execute(job)
        except asyncio.CancelledError:
            pass
        finally:
            self._finish(job)


def _now() -> dt.datetime:
    return dt.datetime.now()


def _to_seconds(value: Union[float, dt.timedelta]) -> float:
    if isinstance(value, dt.timedelta):
        return value.total_seconds()
    return float(value)


def _delay_seconds(when: TimeSpec) -> float:
    """Seconds from now until when, where when may be a delay or an absolute time."""
    if isinstance(when, dt.datetime):
        return max(0.0, (when - _now()).total_seconds())
    return _to_seconds(when)


def _seconds_until_daily(time: dt.time, now: dt.datetime) -> float:
    """Seconds from now until the next occurrence of a daily time."""
    target = now.replace(
        hour=time.hour,
        minute=time.minute,
        second=time.second,
        microsecond=time.microsecond,
    )
    if target <= now:
        target += dt.timedelta(days=1)
    return (target - now).total_seconds()


def _next_monthly(now: dt.datetime, day: int, time: dt.time) -> dt.datetime:
    """The next datetime on the given day-of-month at the given time, after now."""
    year, month = now.year, now.month
    for _ in range(60):
        try:
            candidate: Optional[dt.datetime] = dt.datetime(
                year,
                month,
                day,
                time.hour,
                time.minute,
                time.second,
                time.microsecond,
            )
        except ValueError:
            candidate = None  # this month has no such day
        if candidate is not None and candidate > now:
            return candidate
        month += 1
        if month > 12:
            month = 1
            year += 1
    raise ValueError("Could not find a next monthly run within five years.")


def _seconds_until_monthly(time: dt.time, day: int, now: dt.datetime) -> float:
    """Seconds from now until the next monthly run on day at time."""
    return (_next_monthly(now, day, time) - now).total_seconds()
