from datetime import datetime
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.core.auth.dependencies import get_telegram_current_user
from src.domain.value_objects.telegram_id import TelegramId
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import BadRequestException, NotFoundException
from src.drivers.rest.schemas.activities import (
    MoodHistoryCreate,
    MoodHistoryResponse,
    MoodHistoryUpdate,
)
from src.use_cases.characters.get_character import GetCharacterByUserUseCase
from src.ports.repositories.healthity.activities import MoodHistoryRepository
from src.use_cases.mood_history.manage_mood_history import (
    CreateMoodHistoryInput,
    CreateMoodHistoryUseCase,
    DeleteMoodHistoryUseCase,
    GetMoodHistoryUseCase,
    ListMoodHistoryForCharacterUseCase,
    UpdateMoodHistoryInput,
    UpdateMoodHistoryUseCase,
)

router = APIRouter(prefix="/mood-history", tags=["Mood History"])


@router.get(
    "/admin",
    response_model=list[MoodHistoryResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_mood_history(
    character_id: UUID = Query(..., description="ID персонажа"),
    limit: int = Query(100, ge=1, le=500),
    _: int = Depends(admin_user_provider),
    use_case: ListMoodHistoryForCharacterUseCase = Depends(
        Provide[ApplicationContainer.list_mood_history_for_character_use_case]
    ),
):
    """Получить историю настроения для персонажа (требуется админ-доступ)"""
    mood_history = await use_case.execute(character_id, limit=limit)
    return [MoodHistoryResponse.model_validate(mh) for mh in mood_history]


@router.get(
    "/{mood_history_id}/admin",
    response_model=MoodHistoryResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_mood_history(
    mood_history_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: GetMoodHistoryUseCase = Depends(
        Provide[ApplicationContainer.get_mood_history_use_case]
    ),
):
    """Получить запись о настроении по ID (требуется админ-доступ)"""
    try:
        mood_history = await use_case.execute(mood_history_id)
        return MoodHistoryResponse.model_validate(mood_history)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/admin", response_model=MoodHistoryResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_mood_history(
    data: MoodHistoryCreate,
    _: int = Depends(admin_user_provider),
    use_case: CreateMoodHistoryUseCase = Depends(
        Provide[ApplicationContainer.create_mood_history_use_case]
    ),
):
    """Создать запись о настроении (требуется админ-доступ)"""
    input_data = CreateMoodHistoryInput(
        character_id=data.character_id,
        mood=data.mood,
        trigger=data.trigger,
    )
    mood_history = await use_case.execute(input_data)
    return MoodHistoryResponse.model_validate(mood_history)


@router.patch(
    "/{mood_history_id}/admin",
    response_model=MoodHistoryResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_mood_history(
    mood_history_id: UUID,
    data: MoodHistoryUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdateMoodHistoryUseCase = Depends(
        Provide[ApplicationContainer.update_mood_history_use_case]
    ),
):
    """Обновить запись о настроении (требуется админ-доступ)"""
    try:
        input_data = UpdateMoodHistoryInput(
            mood_history_id=mood_history_id,
            mood=data.mood,
            trigger=data.trigger,
        )
        mood_history = await use_case.execute(input_data)
        return MoodHistoryResponse.model_validate(mood_history)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{mood_history_id}/admin", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_mood_history(
    mood_history_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: DeleteMoodHistoryUseCase = Depends(
        Provide[ApplicationContainer.delete_mood_history_use_case]
    ),
):
    """Удалить запись о настроении (требуется админ-доступ)"""
    try:
        await use_case.execute(mood_history_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get("/me", response_model=list[MoodHistoryResponse])
@inject
async def get_my_mood_history(
    day: datetime | None = Query(
        None,
        description="День для получения истории настроения",
        example="2025-10-25 00:00:00",
    ),
    start_date: datetime | None = Query(
        None, description="Начальная дата диапазона", example="2025-10-01 00:00:00"
    ),
    end_date: datetime | None = Query(
        None, description="Конечная дата диапазона", example="2025-10-31 23:59:59"
    ),
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: ListMoodHistoryForCharacterUseCase = Depends(
        Provide[ApplicationContainer.list_mood_history_for_character_use_case]
    ),
    mood_repo: MoodHistoryRepository = Depends(
        Provide[ApplicationContainer.mood_history_repository]
    ),
):
    """Получить историю настроения за день или диапазон дат"""

    # Валидация параметров
    if day is not None and (start_date is not None or end_date is not None):
        raise BadRequestException("Нельзя указывать day вместе с start_date/end_date")

    if start_date is not None and end_date is None:
        raise BadRequestException(
            "Если указана start_date, то end_date тоже обязательна"
        )

    if end_date is not None and start_date is None:
        raise BadRequestException(
            "Если указана end_date, то start_date тоже обязательна"
        )

    if day is None and start_date is None and end_date is None:
        raise BadRequestException(
            "Необходимо указать либо day, либо start_date и end_date"
        )

    try:
        character = await get_character_use_case.execute(telegram_id.value)

        if day is not None:
            # Получаем историю настроения за конкретный день
            mood_history = await mood_repo.list_for_date_range(character.id, day, day)
        else:
            # Получаем историю настроения за диапазон дат
            mood_history = await mood_repo.list_for_date_range(
                character.id, start_date, end_date
            )

        return [MoodHistoryResponse.model_validate(mh) for mh in mood_history]
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/me", response_model=MoodHistoryResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_my_mood_entry(
    mood: str = Query(..., description="Настроение"),
    trigger: str | None = Query(None, description="Триггер"),
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: CreateMoodHistoryUseCase = Depends(
        Provide[ApplicationContainer.create_mood_history_use_case]
    ),
):
    """Создать запись о настроении для текущего пользователя"""

    try:
        character = await get_character_use_case.execute(telegram_id.value)

        input_data = CreateMoodHistoryInput(
            character_id=character.id,
            mood=mood,
            trigger=trigger,
        )
        mood_history = await use_case.execute(input_data)
        return MoodHistoryResponse.model_validate(mood_history)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))
