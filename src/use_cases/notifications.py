import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from src.adapters.redis.notification_store import (
    deactivate_user_notifications,
    get_user_notification_settings,
    set_user_notification_settings,
)
from src.infrastructure.messaging.notification_scheduling import schedule_notification_at
from src.infrastructure.messaging.broker import schedule_source

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Start / update notifications
# ---------------------------------------------------------------------------


@dataclass
class StartNotificationsInput:
    user_id: int
    interval_minutes: int


@dataclass
class StartNotificationsResult:
    user_id: int
    interval_minutes: int
    schedule_id: str
    is_active: bool


class StartNotificationsUseCase:
    """
    Activates (or updates) periodic notifications for a user.

    Uses one-shot ``time=`` schedules (not cron) so the first message is sent
    ``interval_minutes`` after this request; each subsequent run is scheduled
    from the worker after delivery (anchored to subscription time, not clock).
    """

    async def execute(self, data: StartNotificationsInput) -> StartNotificationsResult:
        if data.interval_minutes <= 0:
            raise ValueError("interval_minutes must be a positive integer")

        existing = await get_user_notification_settings(data.user_id)

        # Remove stale schedule so it does not fire after the update.
        if existing and existing.get("schedule_id"):
            try:
                await schedule_source.delete_schedule(existing["schedule_id"])
                logger.info(
                    "Deleted old schedule %s for user %s",
                    existing["schedule_id"],
                    data.user_id,
                )
            except Exception:
                logger.warning(
                    "Could not delete old schedule for user %s — it may have already expired",
                    data.user_id,
                )

        schedule_id = str(uuid.uuid4())
        first_at = datetime.now(timezone.utc) + timedelta(minutes=data.interval_minutes)

        await schedule_notification_at(first_at, data.user_id, schedule_id)

        await set_user_notification_settings(
            user_id=data.user_id,
            interval_minutes=data.interval_minutes,
            schedule_id=schedule_id,
        )

        logger.info(
            "Notifications started for user %s: every %s min (schedule=%s, first_at=%s)",
            data.user_id,
            data.interval_minutes,
            schedule_id,
            first_at.isoformat(),
        )
        return StartNotificationsResult(
            user_id=data.user_id,
            interval_minutes=data.interval_minutes,
            schedule_id=schedule_id,
            is_active=True,
        )


# ---------------------------------------------------------------------------
# Stop notifications
# ---------------------------------------------------------------------------


@dataclass
class StopNotificationsInput:
    user_id: int


@dataclass
class StopNotificationsResult:
    user_id: int
    is_active: bool


class StopNotificationsUseCase:
    """
    Deactivates periodic notifications for a user.

    Deletes the ScheduledTask from Redis so no further dispatches occur,
    and marks the subscription as inactive in case a race-condition task
    is already in flight.
    """

    async def execute(self, data: StopNotificationsInput) -> StopNotificationsResult:
        existing = await get_user_notification_settings(data.user_id)

        if existing and existing.get("schedule_id"):
            try:
                await schedule_source.delete_schedule(existing["schedule_id"])
                logger.info(
                    "Deleted schedule %s for user %s",
                    existing["schedule_id"],
                    data.user_id,
                )
            except Exception:
                logger.warning(
                    "Could not delete schedule for user %s — may already be gone",
                    data.user_id,
                )

        await deactivate_user_notifications(data.user_id)
        logger.info("Notifications stopped for user %s", data.user_id)
        return StopNotificationsResult(user_id=data.user_id, is_active=False)


# ---------------------------------------------------------------------------
# Get notification status
# ---------------------------------------------------------------------------


@dataclass
class NotificationStatusResult:
    user_id: int
    is_active: bool
    interval_minutes: int | None
    schedule_id: str | None
    last_sent_at: datetime | None


class GetNotificationStatusUseCase:
    async def execute(self, user_id: int) -> NotificationStatusResult:
        data = await get_user_notification_settings(user_id)
        if data is None:
            return NotificationStatusResult(
                user_id=user_id,
                is_active=False,
                interval_minutes=None,
                schedule_id=None,
                last_sent_at=None,
            )

        last_sent_at: datetime | None = None
        raw_ts = data.get("last_sent_at")
        if raw_ts:
            last_sent_at = datetime.fromisoformat(raw_ts)

        return NotificationStatusResult(
            user_id=user_id,
            is_active=data.get("is_active", False),
            interval_minutes=data.get("interval_minutes"),
            schedule_id=data.get("schedule_id"),
            last_sent_at=last_sent_at,
        )
