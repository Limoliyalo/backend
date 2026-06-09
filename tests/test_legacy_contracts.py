import asyncio
import inspect
import uuid
from datetime import datetime
from types import SimpleNamespace

from src.domain.entities.healthity.characters import CharacterBackground, CharacterItem
from src.domain.entities.healthity.users import User
from src.drivers.rest.exceptions import BadRequestException
from src.drivers.rest.schemas.activities import DailyProgressUserCreate
from src.drivers.rest.schemas.notifications import StartNotificationRequest
from src.drivers.rest.schemas.user_friends import FriendInfoResponse
from src.drivers.rest.schemas.users import UserRegister, UserResponse
from src.drivers.rest import user_friends
from src.drivers.rest.users import register_user, router as users_router


class RecordingCreateUserUseCase:
    def __init__(self) -> None:
        self.input_data = None

    async def execute(self, data):
        self.input_data = data
        return User(
            telegram_id=data.telegram_id,
            password_hash="stored-hash",
            is_active=data.is_active,
            is_admin=data.is_admin,
            balance=data.balance,
        )


def test_user_response_excludes_password_hash_from_api_clients() -> None:
    response = UserResponse.model_validate(
        User(telegram_id=111, password_hash="stored-hash")
    ).model_dump()

    assert "password_hash" not in response


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


def test_registration_rejects_body_telegram_id_that_does_not_match_auth() -> None:
    use_case = RecordingCreateUserUseCase()

    async def run() -> None:
        try:
            await register_user(
                UserRegister(telegram_id=111),
                telegram_id=222,
                use_case=use_case,
            )
        except BadRequestException as exc:
            assert exc.detail == "Telegram user mismatch"
        else:
            raise AssertionError("registration accepted an unverified Telegram ID")

        assert use_case.input_data is None

    asyncio.run(run())


def test_registration_marks_configured_admin_only_after_auth_match(monkeypatch) -> None:
    monkeypatch.setenv("APPLICATION_ADMIN_TELEGRAM_IDS", "111")

    from src.core.settings import get_settings

    get_settings.cache_clear()
    use_case = RecordingCreateUserUseCase()

    async def run() -> None:
        response = await register_user(
            UserRegister(telegram_id=111),
            telegram_id=111,
            use_case=use_case,
        )

        assert response.telegram_id == 111
        assert use_case.input_data is not None
        assert use_case.input_data.telegram_id == 111
        assert use_case.input_data.is_admin is True

    asyncio.run(run())
    get_settings.cache_clear()


def test_users_router_does_not_expose_self_service_deposit_route() -> None:
    assert all(route.path != "/users/me/deposit" for route in users_router.routes)


def test_friend_info_response_does_not_include_sensitive_history_fields() -> None:
    assert "mood_history" not in FriendInfoResponse.model_fields
    assert "transactions" not in FriendInfoResponse.model_fields


def test_friend_info_endpoint_does_not_depend_on_sensitive_history_repositories() -> None:
    parameters = inspect.signature(user_friends.get_friend_info).parameters

    assert "mood_repo" not in parameters
    assert "transactions_repo" not in parameters
