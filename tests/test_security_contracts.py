import asyncio
import logging
import uuid
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.security import HTTPBasicCredentials
from pydantic import ValidationError

from src.core.auth.admin import admin_user_provider
from src.core.security import PasswordHasher
from src.core.settings import Settings
from src.domain.entities.healthity.activities import DailyProgress
from src.domain.entities.healthity.catalog import Background, Item
from src.domain.entities.healthity.characters import (
    Character,
    CharacterBackground,
    CharacterItem,
)
from src.domain.entities.healthity.users import User
from src.drivers.rest.exceptions import ForbiddenException, UnauthorizedException
from src.drivers.rest.daily_progress import create_or_update_daily_progress
from src.drivers.rest.schemas.activities import DailyProgressUserCreate
from src.drivers.rest.schemas.notifications import (
    MAX_NOTIFICATION_INTERVAL_MINUTES,
    StartNotificationRequest,
)
from src.drivers.rest.schemas.users import DepositRequest, UserRegister, UserResponse
from src.drivers.rest.users import deposit, register_user
from src.use_cases.character_backgrounds.manage_character_backgrounds import (
    PurchaseBackgroundWithBalanceInput,
    PurchaseBackgroundWithBalanceUseCase,
)
from src.use_cases.character_items.manage_character_items import (
    PurchaseItemWithBalanceInput,
    PurchaseItemWithBalanceUseCase,
)


ROOT = Path(__file__).resolve().parents[1]


class RecordingCreateUserUseCase:
    def __init__(self) -> None:
        self.called = False

    async def execute(self, data):
        self.called = True
        return User(telegram_id=data.telegram_id, password_hash="stored-hash")


class MissingUsersRepository:
    async def get_by_telegram_id(self, telegram_id: int):
        return None


class StaticUsersRepository:
    def __init__(self, user: User) -> None:
        self.user = user

    async def get_by_telegram_id(self, telegram_id: int):
        return self.user if self.user.telegram_id == telegram_id else None

    async def update(self, user: User):
        self.user = user
        return user


class StaticCharactersRepository:
    def __init__(self, character: Character) -> None:
        self.character = character

    async def get_by_id(self, character_id: uuid.UUID):
        return self.character if self.character.id == character_id else None


class StaticCatalogRepository:
    def __init__(self, entity) -> None:
        self.entity = entity

    async def get(self, entity_id: uuid.UUID):
        return self.entity if self.entity.id == entity_id else None


class RecordingInventoryRepository:
    def __init__(self) -> None:
        self.added = []
        self.updated = []
        self.purchase_called = False

    async def list_for_character(self, character_id: uuid.UUID):
        return []

    async def add(self, entity):
        self.added.append(entity)
        return entity

    async def update(self, entity):
        self.updated.append(entity)
        return entity

    async def purchase_with_balance(self, **kwargs):
        self.purchase_called = True
        raise AssertionError("purchase_with_balance should not be called")


class RecordingTransactionsRepository:
    def __init__(self) -> None:
        self.added = []

    async def add(self, transaction):
        self.added.append(transaction)
        return transaction


class StaticCharacterByUserUseCase:
    def __init__(self, character: Character) -> None:
        self.character = character

    async def execute(self, telegram_id: int):
        return self.character


class RecordingCreateDailyProgressUseCase:
    def __init__(self, character: Character) -> None:
        self.character = character
        self.input_data = None

    async def execute(self, data):
        self.input_data = data
        return DailyProgress(
            id=uuid.uuid4(),
            character_id=self.character.id,
            date=data.date,
            experience_gained=data.experience_gained,
            mood_average=data.mood_average,
            behavior_index=data.behavior_index,
        )


def minimal_settings(**overrides) -> Settings:
    data = {
        "db_host": "localhost",
        "db_port": 5432,
        "db_name": "healthity_test",
        "db_user": "healthity_test",
        "db_password": "healthity_test",
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_password": None,
        "rabbit_host": "localhost",
        "rabbit_port": 5672,
        "rabbit_web_port": 15672,
        "rabbit_user": "guest",
        "rabbit_password": "guest",
        "jwt_secret_key": "test-secret",
        "jwt_algorithm": "HS256",
        "jwt_access_token_expire_minutes": 15,
        "jwt_refresh_token_expire_minutes": 43200,
        "telegram_bot_token": "123456:test-token",
    }
    data.update(overrides)
    return Settings(**data)


def test_register_allows_legacy_client_telegram_id_registration() -> None:
    use_case = RecordingCreateUserUseCase()

    async def run() -> None:
        await register_user(
            UserRegister(telegram_id=111),
            use_case=use_case,
        )

    asyncio.run(run())

    assert use_case.called is True


def test_self_service_deposit_is_disabled() -> None:
    async def run() -> None:
        await deposit(DepositRequest(amount=1), telegram_id=111)

    with pytest.raises(ForbiddenException):
        asyncio.run(run())


def test_user_response_never_serializes_password_hash() -> None:
    response = UserResponse.model_validate(
        User(telegram_id=111, password_hash="stored-hash")
    ).model_dump()

    assert "password_hash" not in response


def test_cors_origins_are_parsed_from_allowlist() -> None:
    settings = minimal_settings(
        cors_allowed_origins=" https://healthity.ru, ,http://localhost:3010 "
    )

    assert settings.cors_origins == [
        "https://healthity.ru",
        "http://localhost:3010",
    ]


def test_admin_auth_failure_logs_do_not_include_submitted_usernames(
    caplog: pytest.LogCaptureFixture,
) -> None:
    credentials = HTTPBasicCredentials(username="123456789", password="bad-password")

    async def run() -> None:
        await admin_user_provider(
            credentials,
            users_repository=MissingUsersRepository(),
            password_hasher=PasswordHasher(),
        )

    with caplog.at_level(logging.WARNING):
        with pytest.raises(UnauthorizedException):
            asyncio.run(run())

    assert credentials.username not in caplog.text


def test_admin_auth_checks_password_before_non_admin_status() -> None:
    hasher = PasswordHasher()
    user = User(
        telegram_id=123456789,
        password_hash=hasher.get_password_hash("correct-password"),
        is_admin=False,
    )
    credentials = HTTPBasicCredentials(username="123456789", password="wrong-password")

    async def run() -> None:
        await admin_user_provider(
            credentials,
            users_repository=StaticUsersRepository(user),
            password_hasher=hasher,
        )

    with pytest.raises(UnauthorizedException):
        asyncio.run(run())


def test_unpurchased_items_and_backgrounds_cannot_be_activated() -> None:
    character_id = uuid.uuid4()

    with pytest.raises(ValueError):
        CharacterItem(
            id=uuid.uuid4(),
            character_id=character_id,
            item_id=uuid.uuid4(),
            is_purchased=False,
        ).equip()

    with pytest.raises(ValueError):
        CharacterBackground(
            id=uuid.uuid4(),
            character_id=character_id,
            background_id=uuid.uuid4(),
            is_purchased=False,
        ).activate()


def test_item_purchase_requires_character_level() -> None:
    character = Character(id=uuid.uuid4(), user_tg_id=123456789, level=1)
    item = Item(
        id=uuid.uuid4(),
        category_id=uuid.uuid4(),
        name="Locked item",
        cost=1,
        required_level=2,
    )
    inventory = RecordingInventoryRepository()
    transactions = RecordingTransactionsRepository()
    use_case = PurchaseItemWithBalanceUseCase(
        character_items_repository=inventory,
        items_repository=StaticCatalogRepository(item),
        characters_repository=StaticCharactersRepository(character),
    )

    async def run() -> None:
        await use_case.execute(
            PurchaseItemWithBalanceInput(
                user_tg_id=123456789,
                character_id=character.id,
                item_id=item.id,
            )
        )

    with pytest.raises(ValueError, match="requires level"):
        asyncio.run(run())

    assert inventory.added == []
    assert inventory.updated == []
    assert inventory.purchase_called is False
    assert transactions.added == []


def test_item_purchase_requires_character_to_belong_to_user() -> None:
    character = Character(id=uuid.uuid4(), user_tg_id=999999999, level=10)
    item = Item(
        id=uuid.uuid4(),
        category_id=uuid.uuid4(),
        name="Owned item",
        cost=1,
        required_level=1,
    )
    inventory = RecordingInventoryRepository()
    transactions = RecordingTransactionsRepository()
    use_case = PurchaseItemWithBalanceUseCase(
        character_items_repository=inventory,
        items_repository=StaticCatalogRepository(item),
        characters_repository=StaticCharactersRepository(character),
    )

    async def run() -> None:
        await use_case.execute(
            PurchaseItemWithBalanceInput(
                user_tg_id=123456789,
                character_id=character.id,
                item_id=item.id,
            )
        )

    with pytest.raises(ValueError, match="belong"):
        asyncio.run(run())

    assert inventory.added == []
    assert inventory.updated == []
    assert inventory.purchase_called is False
    assert transactions.added == []


def test_background_purchase_requires_character_level() -> None:
    character = Character(id=uuid.uuid4(), user_tg_id=123456789, level=1)
    background = Background(
        id=uuid.uuid4(),
        name="Locked background",
        cost=1,
        required_level=2,
    )
    inventory = RecordingInventoryRepository()
    transactions = RecordingTransactionsRepository()
    use_case = PurchaseBackgroundWithBalanceUseCase(
        character_backgrounds_repository=inventory,
        backgrounds_repository=StaticCatalogRepository(background),
        characters_repository=StaticCharactersRepository(character),
    )

    async def run() -> None:
        await use_case.execute(
            PurchaseBackgroundWithBalanceInput(
                user_tg_id=123456789,
                character_id=character.id,
                background_id=background.id,
            )
        )

    with pytest.raises(ValueError, match="requires level"):
        asyncio.run(run())

    assert inventory.added == []
    assert inventory.updated == []
    assert inventory.purchase_called is False
    assert transactions.added == []


def test_user_daily_progress_cannot_supply_experience_gain() -> None:
    assert "experience_gained" not in DailyProgressUserCreate.model_fields

    character = Character(id=uuid.uuid4(), user_tg_id=123456789)
    use_case = RecordingCreateDailyProgressUseCase(character)
    progress_date = datetime(2026, 6, 5, 12, 0, 0)

    async def run() -> None:
        await create_or_update_daily_progress(
            DailyProgressUserCreate.model_validate(
                {
                    "date": progress_date,
                    "experience_gained": 999,
                    "mood_average": "happy",
                }
            ),
            telegram_id=123456789,
            get_character_use_case=StaticCharacterByUserUseCase(character),
            use_case=use_case,
        )

    asyncio.run(run())

    assert use_case.input_data is not None
    assert use_case.input_data.experience_gained == 0


def test_notification_interval_has_upper_bound() -> None:
    request = StartNotificationRequest(
        notification_time=MAX_NOTIFICATION_INTERVAL_MINUTES
    )

    assert request.notification_time == MAX_NOTIFICATION_INTERVAL_MINUTES

    with pytest.raises(ValidationError):
        StartNotificationRequest(
            notification_time=MAX_NOTIFICATION_INTERVAL_MINUTES + 1
        )


def test_api_documentation_does_not_embed_sensitive_auth_examples() -> None:
    docs = (ROOT / "API_DOCUMENTATION.md").read_text()
    user_progress_request_body = docs.split("POST /daily-progress/me", 1)[1].split(
        "**Примечание:** пользовательский endpoint", 1
    )[0]

    assert "Authorization: Bearer query_id=" not in docs
    assert "experience_gained" not in user_progress_request_body
