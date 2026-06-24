"""Tests for the JobQueue."""
from __future__ import annotations

import asyncio
import datetime as dt
from typing import Any

from moonlygram.ext import (
    Application,
    Job,
    JobQueue,
    MessageHandler,
    filters,
)
from conftest import (
    _msg,
    _update,
    fake_bot,
)


async def test_job_queue_run_once_executes_with_context():
    bot, _ = fake_bot()
    jq = JobQueue()
    Application(bot, job_queue=jq)
    jq.start()
    seen: dict[str, Any] = {}

    async def job(context):
        seen["data"] = context.job.data
        seen["bot"] = context.bot
        seen["jq"] = context.job_queue

    jq.run_once(job, 0.01, data={"k": 1})
    await asyncio.sleep(0.05)

    assert seen["data"] == {"k": 1}
    assert seen["bot"] is bot
    assert seen["jq"] is jq
    assert jq.jobs() == []  # one-shot job removed itself after running


async def test_job_queue_run_repeating_until_removed():
    bot, _ = fake_bot()
    jq = JobQueue()
    Application(bot, job_queue=jq)
    jq.start()
    counter = {"n": 0}

    async def tick(context):
        counter["n"] += 1

    job = jq.run_repeating(tick, 0.02, first=0)
    assert isinstance(job, Job)
    await asyncio.sleep(0.07)
    job.schedule_removal()
    at_removal = counter["n"]
    await asyncio.sleep(0.05)

    assert at_removal >= 2
    assert counter["n"] - at_removal <= 1  # stopped firing after removal


async def test_job_scheduled_before_start_runs_after_start():
    bot, _ = fake_bot()
    jq = JobQueue()
    Application(bot, job_queue=jq)
    ran = {"x": False}

    async def job(context):
        ran["x"] = True

    jq.run_once(job, 0.01)  # registered before the queue is running
    await asyncio.sleep(0.03)
    assert ran["x"] is False
    jq.start()
    await asyncio.sleep(0.03)
    assert ran["x"] is True


async def test_job_error_routed_to_error_handler():
    bot, _ = fake_bot()
    jq = JobQueue()
    app = Application(bot, job_queue=jq)
    jq.start()
    errors: list[Any] = []

    async def bad_job(context):
        raise RuntimeError("job boom")

    async def on_error(update, context):
        errors.append((update, context.error, context.job))

    app.add_error_handler(on_error)
    jq.run_once(bad_job, 0.01)
    await asyncio.sleep(0.05)

    assert len(errors) == 1
    update, error, job = errors[0]
    assert update is None
    assert isinstance(error, RuntimeError)
    assert job is not None and job.name == "bad_job"


async def test_context_job_queue_lets_handler_schedule_a_job():
    bot, _ = fake_bot()
    jq = JobQueue()
    app = Application(bot, job_queue=jq)
    jq.start()
    scheduled: dict[str, Any] = {}

    async def later(context):
        scheduled["ran"] = True

    async def on_msg(update, context):
        context.job_queue.run_once(later, 0.01)

    app.add_handler(MessageHandler(filters.all, on_msg))
    await app.process_update(_update(_msg("hi")))
    await asyncio.sleep(0.05)

    assert scheduled.get("ran") is True


async def test_job_queue_stop_cancels_jobs():
    bot, _ = fake_bot()
    jq = JobQueue()
    Application(bot, job_queue=jq)
    jq.start()
    counter = {"n": 0}

    async def tick(context):
        counter["n"] += 1

    jq.run_repeating(tick, 0.02, first=0)
    await asyncio.sleep(0.03)
    await jq.stop()
    after_stop = counter["n"]
    await asyncio.sleep(0.05)

    assert jq.jobs() == []
    assert counter["n"] == after_stop


def test_seconds_until_daily():
    from moonlygram.ext.jobqueue import _seconds_until_daily

    now = dt.datetime(2026, 6, 23, 10, 0, 0)
    assert _seconds_until_daily(dt.time(10, 30), now) == 1800
    assert _seconds_until_daily(dt.time(9, 0), now) == 23 * 3600


def test_next_monthly_skips_short_months():
    from moonlygram.ext.jobqueue import _next_monthly

    # From Feb 1, the next "day 31" is March 31 (February has no 31st).
    nxt = _next_monthly(dt.datetime(2026, 2, 1, 0, 0, 0), 31, dt.time(10, 0))
    assert (nxt.year, nxt.month, nxt.day, nxt.hour) == (2026, 3, 31, 10)


def test_next_monthly_same_month_when_future():
    from moonlygram.ext.jobqueue import _next_monthly

    nxt = _next_monthly(dt.datetime(2026, 6, 10, 0, 0, 0), 15, dt.time(9, 0))
    assert (nxt.month, nxt.day, nxt.hour) == (6, 15, 9)
