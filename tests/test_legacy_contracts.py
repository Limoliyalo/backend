import asyncio
import uuid
from datetime import datetime
from types import SimpleNamespace

from src.domain.entities.healthity.characters import CharacterBackground, CharacterItem
from src.domain.entities.healthity.users import User
from src.drivers.rest.schemas.activities import DailyProgressUserCreate
from src.drivers.rest.schemas.notifications import StartNotificationRequest
from src.drivers.rest.schemas.users import DepositRequest, UserResponse
from src.drivers.rest.users import deposit


class RecordingDepositUseCase:
    def __init__(self) -> None:
        self.input_data = None

    async def execute(self, data):
        self.input_data = data
        return SimpleNamespace(
            telegram_id=data.telegram_id,
            balance=123,
            updated_at=datetime(2026, 6, 5, 12, 0, 0),
        )


def test_user_response_includes_password_hash_for_legacy_clients() -> None:
    response = UserResponse.model_validate(
        User(telegram_id=111, password_hash="stored-hash")
    ).model_dump()

    assert response["password_hash"] == "stored-hash"


def test_user_daily_progress_accepts_experience_gain() -> None:
    progress = DailyProgressUserCreate(
        date=datetime(2026, 6, 5, 12, 0, 0),
        experience_gained=50,
        mood_average="happy",
    )

    assert progress.experience_gained == 50


def test_notification_interval_has_no_one_day_cap() -> None:
    request = StartNotificationRequest(notification_time=24 * 60 + 1)

    assert request.notification_time == 24 * 60 + 1


def test_unpurchased_character_assets_can_be_activated() -> None:
    character_id = uuid.uuid4()
    item = CharacterItem(
        id=uuid.uuid4(),
        character_id=character_id,
        item_id=uuid.uuid4(),
    )
    background = CharacterBackground(
        id=uuid.uuid4(),
        character_id=character_id,
        background_id=uuid.uuid4(),
    )

    item.equip()
    background.activate()

    assert item.is_active is True
    assert background.is_active is True


def test_self_service_deposit_uses_deposit_use_case() -> None:
    use_case = RecordingDepositUseCase()

    async def run() -> None:
        response = await deposit(
            DepositRequest(amount=25),
            telegram_id=111,
            use_case=use_case,
        )

        assert response.telegram_id == 111
        assert response.balance == 123
        assert use_case.input_data.telegram_id == 111
        assert use_case.input_data.amount == 25

    asyncio.run(run())
