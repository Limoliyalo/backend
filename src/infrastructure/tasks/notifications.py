import logging
import uuid
from datetime import datetime, time, timedelta, timezone
from html import escape

from src.adapters.database.session import session_manager
from src.adapters.database.uow import SQLAlchemyUnitOfWork
from src.adapters.redis.notification_store import (
    get_user_notification_settings,
    update_last_sent_at,
    update_schedule_id,
)
from src.adapters.repositories.healthity.users import SQLAlchemyUserSettingsRepository
from src.infrastructure.messaging.notification_scheduling import schedule_notification_at
from src.infrastructure.messaging.broker import broker
from src.infrastructure.telegram.client import send_telegram_message

logger = logging.getLogger(__name__)
DEFAULT_NOTIFICATION_TEMPLATE = "⏰ Напоминание по расписанию каждые {interval} мин."


def _uow_factory() -> SQLAlchemyUnitOfWork:
    return SQLAlchemyUnitOfWork(session_factory=session_manager.async_session)


def _is_quiet_time(now: time, start: time, end: time) -> bool:
    if start <= end:
        return start <= now < end
    # overnight range, e.g. 23:00 – 02:00
    return now >= start or now < end


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        logger.warning("Invalid notification next_run_at value: %s", value)
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _get_notification_text(data: dict, interval: int) -> str:
    message = data.get("notification_message")
    if isinstance(message, str) and message.strip():
        return escape(message.strip())
    return DEFAULT_NOTIFICATION_TEMPLATE.format(interval=interval)


def _get_next_planned_run_at(data: dict, interval: int, now: datetime) -> datetime:
    interval_delta = timedelta(minutes=interval)
    previous_slot = _parse_datetime(data.get("next_run_at")) or now
    next_at = previous_slot + interval_delta

    while next_at <= now:
        next_at += interval_delta

    return next_at


@broker.task
async def send_notification_task(user_id: int) -> None:
    """
    Sends one notification and, if still subscribed, schedules the next run at
    the next planned interval slot (anchored chain, not wall-clock cron).
    """
    data = await get_user_notification_settings(user_id)

    if not data:
        logger.warning("No notification settings found for user %s — skipping", user_id)
        return

    if not data.get("is_active"):
        logger.info("Notifications inactive for user %s — skipping", user_id)
        return

    interval = data["interval_minutes"]
    now = datetime.now(timezone.utc)

    repo = SQLAlchemyUserSettingsRepository(uow_factory=_uow_factory)
    user_settings = await repo.get_by_user(user_id)
    today = now.strftime("%A").lower()

    if user_settings and user_settings.do_not_disturb:
        logger.info("Do not disturb enabled for user %s — skipping send", user_id)
    elif user_settings and today in user_settings.muted_days:
        logger.info("Muted day %s for user %s — skipping send", today, user_id)
    elif (
        user_settings
        and user_settings.quiet_start_time is not None
        and user_settings.quiet_end_time is not None
        and _is_quiet_time(
            now.time(),
            user_settings.quiet_start_time,
            user_settings.quiet_end_time,
        )
    ):
        logger.info("Quiet hours for user %s — skipping send", user_id)
    else:
        text = _get_notification_text(data, interval)
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
    next_at = _get_next_planned_run_at(data, interval, now)
    await schedule_notification_at(next_at, user_id, next_schedule_id)
    await update_schedule_id(user_id, next_schedule_id, next_at)
    logger.info(
        "Scheduled next notification for user %s at %s (schedule_id=%s)",
        user_id,
        next_at.isoformat(),
        next_schedule_id,
    )
