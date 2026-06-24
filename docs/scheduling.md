# Scheduling jobs

Every `Application` has a dependency-free `JobQueue` (no APScheduler). It starts and stops with
the app; reach it as `app.job_queue`, or in a handler as `context.job_queue`.

```python
async def remind(context):
    await context.bot.send_message(context.job.chat_id, "Time's up!")


async def start_timer(update, context):
    context.job_queue.run_once(remind, 60, chat_id=update.effective_chat_id)
```

A job callback takes a single `context` with `context.job` set. Pass per-job state through
`data=` and read it back as `context.job.data`.

## Scheduling methods

- `run_once(callback, when, *, data, name, chat_id, user_id)` — once after `when` (seconds, a
  `timedelta`, or an absolute `datetime`).
- `run_repeating(callback, interval, *, first=None, ...)` — every `interval` (seconds or a
  `timedelta`); the first run is after `first` (default: one interval).
- `run_daily(callback, time, ...)` — every day at a `datetime.time`.
- `run_monthly(callback, when, day, ...)` — on `day` of each month at a `datetime.time`.

Each returns a `Job`. Stop a recurring job with `job.schedule_removal()`, and look jobs up by
name with `app.job_queue.get_jobs_by_name("...")`.
