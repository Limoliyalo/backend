from datetime import datetime

from taskiq.kicker import AsyncKicker

from src.infrastructure.messaging.broker import broker, schedule_source

# Must match Taskiq registration: "{module}:{function}"
DAILY_REWARD_TASK_NAME = "src.infrastructure.tasks.daily_rewards:daily_reward_task"


async def schedule_daily_reward_at(run_at: datetime, schedule_id: str) -> None:
    """
    Enqueue a single fire of daily_reward_task at ``run_at`` (timezone-aware UTC).
    """
    kicker = AsyncKicker(DAILY_REWARD_TASK_NAME, broker, {})
    await kicker.with_schedule_id(schedule_id).with_task_id(schedule_id).schedule_by_time(
        schedule_source,
        run_at,
    )

