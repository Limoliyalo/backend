import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from src.drivers.rest.schemas.notifications import StartNotificationRequest
from src.use_cases import notifications as notification_use_cases
from src.infrastructure.tasks import notifications as notification_tasks


class FrozenDateTime(datetime):
    fixed_now: datetime

    @classmethod
    def now(cls, tz=None):
        if tz is None:
            return cls.fixed_now.replace(tzinfo=None)
        return cls.fixed_now.astimezone(tz)


def test_notification_message_is_trimmed_and_blank_becomes_none() -> None:
    request = StartNotificationRequest(
        notification_time=5,
        notification_message="  Пора встать  ",
    )
    blank_request = StartNotificationRequest(
        notification_time=5,
        notification_message="   ",
    )

    assert request.notification_message == "Пора встать"
    assert blank_request.notification_message is None


def test_notification_message_has_200_character_limit() -> None:
    request = StartNotificationRequest(
        notification_time=5,
        notification_message="a" * 200,
    )

    assert request.notification_message == "a" * 200

    with pytest.raises(ValidationError):
        StartNotificationRequest(
            notification_time=5,
            notification_message="a" * 201,
        )


def test_start_notifications_schedules_first_run_from_now_and_persists_message(
    monkeypatch,
) -> None:
    now = datetime(2026, 6, 5, 14, 7, tzinfo=timezone.utc)
    FrozenDateTime.fixed_now = now
    scheduled: list[tuple[datetime, int, str]] = []
    saved: dict[str, object] = {}

    async def get_existing(user_id: int):
        return None

    async def schedule_at(run_at: datetime, user_id: int, schedule_id: str) -> None:
        scheduled.append((run_at, user_id, schedule_id))

    async def save_settings(
        *,
        user_id: int,
        interval_minutes: int,
        schedule_id: str,
        notification_message: str | None,
        next_run_at: datetime,
    ) -> None:
        saved.update(
            {
                "user_id": user_id,
                "interval_minutes": interval_minutes,
                "schedule_id": schedule_id,
                "notification_message": notification_message,
                "next_run_at": next_run_at,
            }
        )

    monkeypatch.setattr(notification_use_cases, "datetime", FrozenDateTime)
    monkeypatch.setattr(notification_use_cases.uuid, "uuid4", lambda: "schedule-1")
    monkeypatch.setattr(notification_use_cases, "get_user_notification_settings", get_existing)
    monkeypatch.setattr(notification_use_cases, "schedule_notification_at", schedule_at)
    monkeypatch.setattr(notification_use_cases, "set_user_notification_settings", save_settings)

    async def run() -> None:
        await notification_use_cases.StartNotificationsUseCase().execute(
            notification_use_cases.StartNotificationsInput(
                user_id=123,
                interval_minutes=5,
                notification_message="Пора встать",
            )
        )

    asyncio.run(run())

    first_at = now + timedelta(minutes=5)
    assert scheduled == [(first_at, 123, "schedule-1")]
    assert saved == {
        "user_id": 123,
        "interval_minutes": 5,
        "schedule_id": "schedule-1",
        "notification_message": "Пора встать",
        "next_run_at": first_at,
    }


def test_worker_reschedules_from_stored_planned_slot_and_uses_custom_message(
    monkeypatch,
) -> None:
    now = datetime(2026, 6, 5, 14, 12, 3, tzinfo=timezone.utc)
    planned_slot = datetime(2026, 6, 5, 14, 12, tzinfo=timezone.utc)
    FrozenDateTime.fixed_now = now
    data = {
        "is_active": True,
        "interval_minutes": 5,
        "schedule_id": "schedule-1",
        "last_sent_at": None,
        "notification_message": "Встать и размяться",
        "next_run_at": planned_slot.isoformat(),
    }
    sent_messages: list[str] = []
    scheduled: list[tuple[datetime, int, str]] = []
    schedule_updates: list[tuple[int, str, datetime]] = []

    async def get_settings(user_id: int):
        return data

    async def send_message(tg_id: int, text: str) -> None:
        sent_messages.append(text)

    async def update_last_sent_at(user_id: int) -> None:
        data["last_sent_at"] = now.isoformat()

    async def schedule_at(run_at: datetime, user_id: int, schedule_id: str) -> None:
        scheduled.append((run_at, user_id, schedule_id))

    async def update_schedule_id(
        user_id: int,
        schedule_id: str,
        next_run_at: datetime,
    ) -> None:
        schedule_updates.append((user_id, schedule_id, next_run_at))

    class NoSettingsRepository:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def get_by_user(self, user_id: int):
            return None

    monkeypatch.setattr(notification_tasks, "datetime", FrozenDateTime)
    monkeypatch.setattr(notification_tasks.uuid, "uuid4", lambda: "schedule-2")
    monkeypatch.setattr(notification_tasks, "get_user_notification_settings", get_settings)
    monkeypatch.setattr(notification_tasks, "send_telegram_message", send_message)
    monkeypatch.setattr(notification_tasks, "update_last_sent_at", update_last_sent_at)
    monkeypatch.setattr(notification_tasks, "schedule_notification_at", schedule_at)
    monkeypatch.setattr(notification_tasks, "update_schedule_id", update_schedule_id)
    monkeypatch.setattr(notification_tasks, "SQLAlchemyUserSettingsRepository", NoSettingsRepository)

    asyncio.run(notification_tasks.send_notification_task.original_func(123))

    next_slot = planned_slot + timedelta(minutes=5)
    assert sent_messages == ["Встать и размяться"]
    assert scheduled == [(next_slot, 123, "schedule-2")]
    assert schedule_updates == [(123, "schedule-2", next_slot)]


def test_worker_skips_missed_slots_when_late(monkeypatch) -> None:
    now = datetime(2026, 6, 5, 14, 31, tzinfo=timezone.utc)
    planned_slot = datetime(2026, 6, 5, 14, 12, tzinfo=timezone.utc)
    FrozenDateTime.fixed_now = now
    data = {
        "is_active": True,
        "interval_minutes": 5,
        "schedule_id": "schedule-1",
        "last_sent_at": None,
        "notification_message": None,
        "next_run_at": planned_slot.isoformat(),
    }
    sent_messages: list[str] = []
    scheduled: list[tuple[datetime, int, str]] = []

    async def get_settings(user_id: int):
        return data

    async def send_message(tg_id: int, text: str) -> None:
        sent_messages.append(text)

    async def update_last_sent_at(user_id: int) -> None:
        pass

    async def schedule_at(run_at: datetime, user_id: int, schedule_id: str) -> None:
        scheduled.append((run_at, user_id, schedule_id))

    async def update_schedule_id(
        user_id: int,
        schedule_id: str,
        next_run_at: datetime,
    ) -> None:
        data["schedule_id"] = schedule_id
        data["next_run_at"] = next_run_at.isoformat()

    class NoSettingsRepository:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def get_by_user(self, user_id: int):
            return None

    monkeypatch.setattr(notification_tasks, "datetime", FrozenDateTime)
    monkeypatch.setattr(notification_tasks.uuid, "uuid4", lambda: "schedule-2")
    monkeypatch.setattr(notification_tasks, "get_user_notification_settings", get_settings)
    monkeypatch.setattr(notification_tasks, "send_telegram_message", send_message)
    monkeypatch.setattr(notification_tasks, "update_last_sent_at", update_last_sent_at)
    monkeypatch.setattr(notification_tasks, "schedule_notification_at", schedule_at)
    monkeypatch.setattr(notification_tasks, "update_schedule_id", update_schedule_id)
    monkeypatch.setattr(notification_tasks, "SQLAlchemyUserSettingsRepository", NoSettingsRepository)

    asyncio.run(notification_tasks.send_notification_task.original_func(123))

    assert sent_messages == ["⏰ Напоминание по расписанию каждые 5 мин."]
    assert scheduled == [
        (datetime(2026, 6, 5, 14, 32, tzinfo=timezone.utc), 123, "schedule-2")
    ]
