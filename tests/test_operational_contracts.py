import asyncio
from datetime import datetime, timezone
from pathlib import Path

from src.infrastructure.tasks import daily_rewards


class FrozenDateTime(datetime):
    fixed_now: datetime

    @classmethod
    def now(cls, tz=None):
        if tz is None:
            return cls.fixed_now.replace(tzinfo=None)
        return cls.fixed_now.astimezone(tz)


def test_daily_reward_task_schedules_one_stable_chain_per_date(monkeypatch) -> None:
    FrozenDateTime.fixed_now = datetime(2026, 6, 19, 14, 0, tzinfo=timezone.utc)
    scheduled: list[tuple[datetime, str]] = []

    class NoopRepository:
        def __init__(self, *args, **kwargs) -> None:
            pass

    class NoopCreateTransactionUseCase:
        def __init__(self, *args, **kwargs) -> None:
            pass

    class NoopRunDailyRewardsUseCase:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def execute(self, data) -> None:
            return None

    async def schedule_daily_reward_at(run_at: datetime, schedule_id: str) -> None:
        scheduled.append((run_at, schedule_id))

    monkeypatch.setattr(daily_rewards, "datetime", FrozenDateTime)
    monkeypatch.setattr(daily_rewards, "SQLAlchemyCharactersRepository", NoopRepository)
    monkeypatch.setattr(
        daily_rewards,
        "SQLAlchemyBaseCharacterActivitiesRepository",
        NoopRepository,
    )
    monkeypatch.setattr(
        daily_rewards,
        "SQLAlchemyDailyActivitiesRepository",
        NoopRepository,
    )
    monkeypatch.setattr(daily_rewards, "SQLAlchemyUsersRepository", NoopRepository)
    monkeypatch.setattr(
        daily_rewards,
        "SQLAlchemyTransactionsRepository",
        NoopRepository,
    )
    monkeypatch.setattr(
        daily_rewards,
        "CreateTransactionUseCase",
        NoopCreateTransactionUseCase,
    )
    monkeypatch.setattr(
        daily_rewards,
        "RunDailyRewardsUseCase",
        NoopRunDailyRewardsUseCase,
    )
    monkeypatch.setattr(
        daily_rewards,
        "schedule_daily_reward_at",
        schedule_daily_reward_at,
    )

    asyncio.run(daily_rewards.daily_reward_task.original_func())

    assert scheduled == [
        (
            datetime(2026, 6, 20, tzinfo=timezone.utc),
            "daily_reward:2026-06-20",
        )
    ]


def test_compose_does_not_publish_internal_services_publicly() -> None:
    root = Path(__file__).resolve().parents[1]
    app_compose = (root / "docker-compose" / "app.yaml").read_text()
    db_compose = (root / "docker-compose" / "db.yaml").read_text()
    nats_compose = (root / "docker-compose" / "nats.yaml").read_text()

    assert '"127.0.0.1:8000:8000"' in app_compose
    assert '"127.0.0.1:5433:5432"' in db_compose
    assert '"127.0.0.1:6378:6379"' in db_compose
    assert '"127.0.0.1:${NATS_PORT:-4222}:4222"' in nats_compose
    assert '"127.0.0.1:${NATS_MONITOR_PORT:-8222}:8222"' in nats_compose

    combined = "\n".join([app_compose, db_compose, nats_compose])
    assert '"8000:8000"' not in combined
    assert '"5433:5432"' not in combined
    assert '"6378:6379"' not in combined
    assert '"${NATS_PORT:-4222}:4222"' not in combined
    assert '"${NATS_MONITOR_PORT:-8222}:8222"' not in combined
