import logging

from src.adapters.redis.notification_store import (
    get_user_notification_settings,
    update_last_sent_at,
)
from src.infrastructure.messaging.broker import broker
from src.infrastructure.telegram.client import send_telegram_message

logger = logging.getLogger(__name__)


@broker.task
async def send_notification_task(user_id: int) -> None:
    """
    Periodic notification task dispatched by TaskiqScheduler every N minutes.

    Checks whether the user's subscription is still active before sending.
    If deactivated, the task exits silently — the scheduler will not dispatch
    more runs because the schedule was already deleted on stop.
    """
    data = await get_user_notification_settings(user_id)

    if not data:
        logger.warning("No notification settings found for user %s — skipping", user_id)
        return

    if not data.get("is_active"):
        logger.info("Notifications inactive for user %s — skipping", user_id)
        return

    interval = data["interval_minutes"]
    text = f"⏰ Напоминание по расписанию каждые {interval} мин."

    try:
        await send_telegram_message(tg_id=user_id, text=text)
        await update_last_sent_at(user_id)
    except Exception:
        logger.exception("Failed to send notification to user %s", user_id)
        raise  # re-raise so Taskiq marks the task as failed
