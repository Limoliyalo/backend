from datetime import datetime
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.core.auth.dependencies import get_telegram_current_user
from src.domain.value_objects.telegram_id import TelegramId
from src.domain.exceptions import EntityNotFoundException
from src.adapters.repositories.exceptions import RepositoryError
from src.drivers.rest.exceptions import NotFoundException, BadRequestException
from src.drivers.rest.schemas.activities import (
    DailyProgressCreate,
    DailyProgressResponse,
    DailyProgressUpdate,
)
from src.use_cases.characters.get_character import GetCharacterByUserUseCase
from src.use_cases.daily_progress.manage_daily_progress import (
    CreateDailyProgressInput,
    CreateDailyProgressUseCase,
    DeleteDailyProgressUseCase,
    GetDailyProgressForDayUseCase,
    GetDailyProgressUseCase,
    ListDailyProgressForCharacterUseCase,
    ListDailyProgressForDateRangeUseCase,
    UpdateDailyProgressInput,
    UpdateDailyProgressUseCase,
)

router = APIRouter(prefix="/daily-progress", tags=["Daily Progress"])


@router.get(
    "/character/{character_id}/admin",
    response_model=list[DailyProgressResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_daily_progress_for_character(
    character_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: ListDailyProgressForCharacterUseCase = Depends(
        Provide[ApplicationContainer.list_daily_progress_for_character_use_case]
    ),
):
    """Получить весь прогресс персонажа (требуется админ-доступ)"""
    try:
        progress_list = await use_case.execute(character_id)
        return [DailyProgressResponse.model_validate(p) for p in progress_list]
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))


@router.get(
    "/character/{character_id}/day/admin",
    response_model=DailyProgressResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_daily_progress_for_day(
    character_id: UUID,
    day: datetime = Query(
        ..., description="День для получения прогресса", example="2025-10-25 00:00:00"
    ),
    _: int = Depends(admin_user_provider),
    use_case: GetDailyProgressForDayUseCase = Depends(
        Provide[ApplicationContainer.get_daily_progress_for_day_use_case]
    ),
):
    """Получить прогресс персонажа за конкретный день (требуется админ-доступ)"""
    try:
        progress = await use_case.execute(character_id, day)
        return DailyProgressResponse.model_validate(progress)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get(
    "/character/{character_id}/date-range/admin",
    response_model=list[DailyProgressResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def get_daily_progress_for_date_range(
    character_id: UUID,
    start_date: datetime = Query(
        ..., description="Начальная дата диапазона", example="2025-10-01 00:00:00"
    ),
    end_date: datetime = Query(
        ..., description="Конечная дата диапазона", example="2025-10-31 23:59:59"
    ),
    _: int = Depends(admin_user_provider),
    use_case: ListDailyProgressForDateRangeUseCase = Depends(
        Provide[ApplicationContainer.list_daily_progress_for_date_range_use_case]
    ),
):
    """Получить прогресс персонажа за диапазон дат (требуется админ-доступ)"""
    try:
        progress_list = await use_case.execute(character_id, start_date, end_date)
        return [DailyProgressResponse.model_validate(p) for p in progress_list]
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get("/{progress_id}/admin", response_model=DailyProgressResponse)
@inject
async def get_daily_progress(
    progress_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: GetDailyProgressUseCase = Depends(
        Provide[ApplicationContainer.get_daily_progress_use_case]
    ),
):
    """Получить дневной прогресс по ID (требуется админ-доступ)"""
    try:
        progress = await use_case.execute(progress_id)
        return DailyProgressResponse.model_validate(progress)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/admin", response_model=DailyProgressResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_daily_progress(
    data: DailyProgressCreate,
    _: int = Depends(admin_user_provider),
    use_case: CreateDailyProgressUseCase = Depends(
        Provide[ApplicationContainer.create_daily_progress_use_case]
    ),
):
    """Создать или обновить дневной прогресс (требуется админ-доступ)"""
    input_data = CreateDailyProgressInput(
        character_id=data.character_id,
        date=data.date,
        experience_gained=data.experience_gained,
        mood_average=data.mood_average,
        behavior_index=data.behavior_index,
    )
    progress = await use_case.execute(input_data)
    return DailyProgressResponse.model_validate(progress)


@router.patch("/{progress_id}/admin", response_model=DailyProgressResponse)
@inject
async def update_daily_progress(
    progress_id: UUID,
    data: DailyProgressUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdateDailyProgressUseCase = Depends(
        Provide[ApplicationContainer.update_daily_progress_use_case]
    ),
):
    """Обновить дневной прогресс (требуется админ-доступ)"""
    try:
        input_data = UpdateDailyProgressInput(
            progress_id=progress_id,
            experience_gained=data.experience_gained,
            mood_average=data.mood_average,
            behavior_index=data.behavior_index,
        )
        progress = await use_case.execute(input_data)
        return DailyProgressResponse.model_validate(progress)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{progress_id}/admin", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_daily_progress(
    progress_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: DeleteDailyProgressUseCase = Depends(
        Provide[ApplicationContainer.delete_daily_progress_use_case]
    ),
):
    """Удалить дневной прогресс (требуется админ-доступ)"""
    try:
        await use_case.execute(progress_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get("/me", response_model=list[DailyProgressResponse])
@inject
async def get_my_progress(
    day: datetime | None = Query(
        None, description="День для получения прогресса", example="2025-10-25 00:00:00"
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
    get_day_use_case: GetDailyProgressForDayUseCase = Depends(
        Provide[ApplicationContainer.get_daily_progress_for_day_use_case]
    ),
    list_range_use_case: ListDailyProgressForDateRangeUseCase = Depends(
        Provide[ApplicationContainer.list_daily_progress_for_date_range_use_case]
    ),
):
    """Получить прогресс своего персонажа за день или диапазон дат"""

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
            # Получаем прогресс за конкретный день
            progress = await get_day_use_case.execute(character.id, day)
            return [DailyProgressResponse.model_validate(progress)] if progress else []
        else:
            # Получаем прогресс за диапазон дат
            progress_list = await list_range_use_case.execute(
                character.id, start_date, end_date
            )
            return [
                DailyProgressResponse.model_validate(progress)
                for progress in progress_list
            ]

    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/me", response_model=DailyProgressResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_or_update_daily_progress(
    date: datetime = Query(
        ..., description="Дата прогресса", example="2025-10-25 00:00:00"
    ),
    experience_gained: int = Query(0, ge=0, description="Полученный опыт"),
    mood_average: str | None = Query(
        None, description="Среднее настроение (neutral, happy, sad, angry, bored)"
    ),
    behavior_index: int | None = Query(
        None, ge=0, le=100, description="Индекс поведения (0-100)"
    ),
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: CreateDailyProgressUseCase = Depends(
        Provide[ApplicationContainer.create_daily_progress_use_case]
    ),
):
    """Создать или обновить дневной прогресс для текущего пользователя"""

    try:
        character = await get_character_use_case.execute(telegram_id.value)

        input_data = CreateDailyProgressInput(
            character_id=character.id,
            date=date,
            experience_gained=experience_gained,
            mood_average=mood_average,
            behavior_index=behavior_index,
        )
        progress = await use_case.execute(input_data)
        return DailyProgressResponse.model_validate(progress)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))
