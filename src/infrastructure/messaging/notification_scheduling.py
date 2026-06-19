"""
One-shot Taskiq schedules anchored to real time (not clock-aligned cron).

Each run schedules the next at now + interval_minutes so e.g. subscribe at 13:47
with 5 min yields 13:52, 13:57, ...
"""

from datetime import datetime

from taskiq.kicker import AsyncKicker

from src.infrastructure.messaging.broker import broker, schedule_source

# Must match Taskiq registration: "{module}:{function}"
NOTIFICATION_TASK_NAME = "src.infrastructure.tasks.notifications:send_notification_task"


async def schedule_notification_at(
    run_at: datetime,
    user_id: int,
    schedule_id: str,
) -> None:
    """
    Enqueue a single fire of send_notification_task at ``run_at`` (timezone-aware UTC).
    """
    kicker: AsyncKicker[..., None] = AsyncKicker(NOTIFICATION_TASK_NAME, broker, {})
    await kicker.with_schedule_id(schedule_id).with_task_id(schedule_id).schedule_by_time(
        schedule_source,
        run_at,
        user_id,
    )
