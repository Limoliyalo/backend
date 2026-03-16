import json
import logging
from datetime import datetime, timezone

from src.adapters.redis.client import get_redis_client

logger = logging.getLogger(__name__)

NOTIFICATION_KEY_TTL = 60 * 60 * 24 * 365  # 1 year — effectively permanent


def _key(user_id: int) -> str:
    return f"user:{user_id}:notification"


async def set_user_notification_settings(
    user_id: int,
    interval_minutes: int,
    schedule_id: str,
) -> None:
    """Persist subscription state for a user. Overwrites any previous entry."""
    redis = get_redis_client()
    payload = {
        "is_active": True,
        "interval_minutes": interval_minutes,
        "schedule_id": schedule_id,
        "last_sent_at": None,
    }
    await redis.set(_key(user_id), json.dumps(payload), ex=NOTIFICATION_KEY_TTL)
    logger.info("Notification settings saved for user %s (interval=%sm)", user_id, interval_minutes)


async def get_user_notification_settings(user_id: int) -> dict | None:
    """Return the stored subscription dict or None if absent."""
    redis = get_redis_client()
    raw = await redis.get(_key(user_id))
    if raw is None:
        return None
    return json.loads(raw)


async def deactivate_user_notifications(user_id: int) -> None:
    """Mark the subscription as inactive without deleting the key."""
    redis = get_redis_client()
    data = await get_user_notification_settings(user_id)
    if data is None:
        return
    data["is_active"] = False
    await redis.set(_key(user_id), json.dumps(data), ex=NOTIFICATION_KEY_TTL)
    logger.info("Notifications deactivated for user %s", user_id)


async def update_last_sent_at(user_id: int) -> None:
    """Record the timestamp of the most recent successful notification delivery."""
    redis = get_redis_client()
    data = await get_user_notification_settings(user_id)
    if data is None:
        return
    data["last_sent_at"] = datetime.now(timezone.utc).isoformat()
    await redis.set(_key(user_id), json.dumps(data), ex=NOTIFICATION_KEY_TTL)
