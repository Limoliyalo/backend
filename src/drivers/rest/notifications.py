import logging

from fastapi import APIRouter, Depends, status

from src.core.auth.dependencies import get_telegram_current_user
from src.drivers.rest.exceptions import BadRequestException
from src.drivers.rest.schemas.notifications import (
    NotificationStatusResponse,
    StartNotificationRequest,
    StartNotificationResponse,
    StopNotificationResponse,
)
from src.use_cases.notifications import (
    GetNotificationStatusUseCase,
    StartNotificationsInput,
    StartNotificationsUseCase,
    StopNotificationsInput,
    StopNotificationsUseCase,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post(
    "/start",
    response_model=StartNotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate periodic Telegram notifications",
)
async def start_notifications(
    data: StartNotificationRequest,
    telegram_id: int = Depends(get_telegram_current_user),
) -> StartNotificationResponse:
    """
    Save subscription to Redis and register a one-shot Taskiq schedule (then chained).
    Telegram user id comes from validated Mini App init data (Authorization), like /me.
    Calling again with a different interval replaces the existing schedule.
    """
    try:
        result = await StartNotificationsUseCase().execute(
            StartNotificationsInput(
                user_id=telegram_id,
                interval_minutes=data.notification_time,
            )
        )
    except ValueError as exc:
        raise BadRequestException(detail=str(exc))

    return StartNotificationResponse(
        user_id=result.user_id,
        interval_minutes=result.interval_minutes,
        schedule_id=result.schedule_id,
        is_active=result.is_active,
    )


@router.post(
    "/stop",
    response_model=StopNotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate periodic Telegram notifications",
)
async def stop_notifications(
    telegram_id: int = Depends(get_telegram_current_user),
) -> StopNotificationResponse:
    """
    Remove the Taskiq schedule from Redis and mark the subscription inactive.
    Any in-flight task will check the is_active flag and exit without sending.
    """
    result = await StopNotificationsUseCase().execute(
        StopNotificationsInput(user_id=telegram_id)
    )
    return StopNotificationResponse(user_id=result.user_id, is_active=result.is_active)


@router.get(
    "/status",
    response_model=NotificationStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get notification subscription status",
)
async def get_notification_status(
    telegram_id: int = Depends(get_telegram_current_user),
) -> NotificationStatusResponse:
    """Return current subscription state: active flag, interval, and last delivery time."""
    result = await GetNotificationStatusUseCase().execute(telegram_id)
    return NotificationStatusResponse(
        user_id=result.user_id,
        is_active=result.is_active,
        interval_minutes=result.interval_minutes,
        schedule_id=result.schedule_id,
        last_sent_at=result.last_sent_at,
    )
