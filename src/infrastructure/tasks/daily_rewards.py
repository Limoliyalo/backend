import logging
from datetime import datetime, timedelta, timezone

from src.adapters.database.session import session_manager
from src.adapters.database.uow import SQLAlchemyUnitOfWork
from src.adapters.repositories.healthity import (
    SQLAlchemyBaseCharacterActivitiesRepository,
    SQLAlchemyCharactersRepository,
    SQLAlchemyDailyActivitiesRepository,
    SQLAlchemyTransactionsRepository,
    SQLAlchemyUsersRepository,
)
from src.infrastructure.messaging.daily_reward_scheduling import (
    daily_reward_schedule_id,
    schedule_daily_reward_at,
)
from src.infrastructure.messaging.broker import broker
from src.use_cases.rewards.daily_reward import RunDailyRewardsInput, RunDailyRewardsUseCase
from src.use_cases.transactions.manage_transactions import (
    CreateTransactionUseCase,
)

logger = logging.getLogger(__name__)


def _uow_factory() -> SQLAlchemyUnitOfWork:
    return SQLAlchemyUnitOfWork(session_factory=session_manager.async_session)


def _next_midnight_utc(now: datetime) -> datetime:
    date_only = now.astimezone(timezone.utc).date()
    tomorrow = date_only + timedelta(days=1)
    return datetime(tomorrow.year, tomorrow.month, tomorrow.day, tzinfo=timezone.utc)


@broker.task
async def daily_reward_task() -> None:
    """
    начисляет монеты за вчера (UTC) и планирует следующий запуск на 00:00 UTC
    """
    now = datetime.now(timezone.utc)
    reward_date = (now - timedelta(days=1)).date()

    characters_repo = SQLAlchemyCharactersRepository(uow_factory=_uow_factory)
    base_activities_repo = SQLAlchemyBaseCharacterActivitiesRepository(uow_factory=_uow_factory)
    daily_activities_repo = SQLAlchemyDailyActivitiesRepository(uow_factory=_uow_factory)
    users_repo = SQLAlchemyUsersRepository(uow_factory=_uow_factory)
    transactions_repo = SQLAlchemyTransactionsRepository(uow_factory=_uow_factory)

    create_transaction_uc = CreateTransactionUseCase(
        transactions_repository=transactions_repo,
        users_repository=users_repo,
    )
    run_rewards_uc = RunDailyRewardsUseCase(
        characters_repository=characters_repo,
        base_activities_repository=base_activities_repo,
        daily_activities_repository=daily_activities_repo,
        create_transaction_use_case=create_transaction_uc,
    )

    logger.info("Running daily rewards for %s", reward_date.isoformat())
    await run_rewards_uc.execute(RunDailyRewardsInput(reward_date=reward_date))

    next_at = _next_midnight_utc(now)
    schedule_id = daily_reward_schedule_id(next_at)
    await schedule_daily_reward_at(next_at, schedule_id)
    logger.info("Scheduled next daily reward at %s (schedule_id=%s)", next_at.isoformat(), schedule_id)
