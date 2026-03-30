import datetime
import logging
import math
import uuid
from dataclasses import dataclass

from src.adapters.repositories.exceptions import DuplicateEntityError, IntegrityConstraintError
from src.domain.entities.healthity.activities import (
    BaseCharacterActivity,
    CharacterActivityHistory,
)
from src.ports.repositories.healthity.activities import (
    BaseCharacterActivitiesRepository,
    DailyActivitiesRepository,
)
from src.ports.repositories.healthity.characters import CharactersRepository
from src.use_cases.transactions.manage_transactions import (
    CreateTransactionInput,
    CreateTransactionUseCase,
)

logger = logging.getLogger(__name__)

BASE_MAX_COINS = 100
MAX_COINS_ACTIVITY_THRESHOLD = 3
MAX_COINS_MULTIPLIER_PER_EXTRA_ACTIVITY = 1.2


def _clamp01(x: float) -> float:
    if x < 0:
        return 0.0
    if x > 1:
        return 1.0
    return x


def _date_only(d: datetime.datetime) -> datetime.datetime:
    if d.tzinfo is not None:
        d = d.replace(tzinfo=None)
    return d.replace(hour=0, minute=0, second=0, microsecond=0)


def _max_coins_for_n_activities(n: int) -> int:
    if n <= MAX_COINS_ACTIVITY_THRESHOLD:
        return BASE_MAX_COINS
    extra = n - MAX_COINS_ACTIVITY_THRESHOLD
    return round(BASE_MAX_COINS * (MAX_COINS_MULTIPLIER_PER_EXTRA_ACTIVITY**extra))


def _completion_for_activity(
    base: BaseCharacterActivity, history: CharacterActivityHistory | None
) -> float:
    value = history.value if history else 0
    goal = history.goal if history else base.goal
    if goal <= 0:
        return 0.0
    return _clamp01(value / goal)


@dataclass
class RunDailyRewardsInput:
    reward_date: datetime.date


class RunDailyRewardsUseCase:
    """
    начисляет daily reward всем персонажам за reward_date (UTC date, yesterday)
    """

    def __init__(
        self,
        characters_repository: CharactersRepository,
        base_activities_repository: BaseCharacterActivitiesRepository,
        daily_activities_repository: DailyActivitiesRepository,
        create_transaction_use_case: CreateTransactionUseCase,
    ) -> None:
        self._characters_repository = characters_repository
        self._base_activities_repository = base_activities_repository
        self._daily_activities_repository = daily_activities_repository
        self._create_transaction_use_case = create_transaction_use_case

    async def execute(self, data: RunDailyRewardsInput) -> None:
        reward_date_dt = datetime.datetime(
            data.reward_date.year,
            data.reward_date.month,
            data.reward_date.day,
            0,
            0,
            0,
        )

        limit = 1000
        offset = 0
        while True:
            characters = await self._characters_repository.list_all(
                limit=limit, offset=offset
            )
            if not characters:
                break

            for character in characters:
                base_activities = await self._base_activities_repository.list_for_character(
                    character.id
                )
                n = len(base_activities)
                if n == 0:
                    continue

                histories = await self._daily_activities_repository.list_for_day(
                    character.id, _date_only(reward_date_dt)
                )
                history_by_type: dict[uuid.UUID, CharacterActivityHistory] = {
                    h.activity_type_id: h for h in histories
                }

                completions = [
                    _completion_for_activity(
                        base,
                        history_by_type.get(base.activity_type_id),
                    )
                    for base in base_activities
                ]
                day_completion = sum(completions) / n if n else 0.0

                max_coins = _max_coins_for_n_activities(n)
                award = round(max_coins * day_completion)
                if award <= 0:
                    continue

                try:
                    await self._create_transaction_use_case.execute(
                        CreateTransactionInput(
                            user_tg_id=character.user_tg_id,
                            amount=award,
                            type="daily_reward",
                            description=f"Daily reward for {data.reward_date.isoformat()} (completion={math.floor(day_completion*100)}%)",
                            reward_date=data.reward_date,
                        )
                    )
                except (DuplicateEntityError, IntegrityConstraintError):
                    # duplicate reward (idempotency)
                    logger.info(
                        "Daily reward already exists for user %s date %s",
                        character.user_tg_id,
                        data.reward_date.isoformat(),
                    )

            offset += limit

