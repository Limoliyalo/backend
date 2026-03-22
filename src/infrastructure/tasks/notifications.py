import logging
import uuid
from datetime import datetime, timedelta, timezone

from src.adapters.redis.notification_store import (
    get_user_notification_settings,
    update_last_sent_at,
    update_schedule_id,
)
from src.infrastructure.messaging.notification_scheduling import schedule_notification_at
from src.infrastructure.messaging.broker import broker
from src.infrastructure.telegram.client import send_telegram_message

logger = logging.getLogger(__name__)


@broker.task
async def send_notification_task(user_id: int) -> None:
    """
    Sends one notification and, if still subscribed, schedules the next run at
    now + interval_minutes (anchored chain, not wall-clock cron).
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
        raise

    # Re-read: user may have hit /stop during send.
    data = await get_user_notification_settings(user_id)
    if not data or not data.get("is_active"):
        logger.info("Subscription ended for user %s — not scheduling next run", user_id)
        return

    next_schedule_id = str(uuid.uuid4())
    next_at = datetime.now(timezone.utc) + timedelta(minutes=interval)
    await schedule_notification_at(next_at, user_id, next_schedule_id)
    await update_schedule_id(user_id, next_schedule_id)
    logger.info(
        "Scheduled next notification for user %s at %s (schedule_id=%s)",
        user_id,
        next_at.isoformat(),
        next_schedule_id,
    )
