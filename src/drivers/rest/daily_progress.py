from datetime import datetime
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.core.auth.dependencies import get_access_token_payload
from src.core.auth.jwt_service import TokenPayload
from src.domain.exceptions import EntityNotFoundException
from src.adapters.repositories.exceptions import RepositoryError
from src.drivers.rest.exceptions import NotFoundException, BadRequestException
from src.drivers.rest.schemas.activities import (
    DailyProgressCreate,
    DailyProgressResponse,
    DailyProgressUpdate,
)
from src.ports.repositories.healthity.activities import DailyProgressRepository
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
    "/character/{character_id}",
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
    "/character/{character_id}/day",
    response_model=DailyProgressResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_daily_progress_for_day(
    character_id: UUID,
    day: datetime = Query(..., description="День для получения прогресса"),
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
    "/character/{character_id}/date-range",
    response_model=list[DailyProgressResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def get_daily_progress_for_date_range(
    character_id: UUID,
    start_date: datetime = Query(..., description="Начальная дата диапазона"),
    end_date: datetime = Query(..., description="Конечная дата диапазона"),
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
async def list_my_daily_progress(
    limit: int = Query(
        30,
        ge=1,
        le=365,
        description="Количество дней (используется если не указан диапазон)",
    ),
    start_date: datetime | None = Query(None, description="Начальная дата диапазона"),
    end_date: datetime | None = Query(None, description="Конечная дата диапазона"),
    payload: TokenPayload = Depends(get_access_token_payload),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: ListDailyProgressForCharacterUseCase = Depends(
        Provide[ApplicationContainer.list_daily_progress_for_character_use_case]
    ),
    progress_repo: DailyProgressRepository = Depends(
        Provide[ApplicationContainer.daily_progress_repository]
    ),
):
    """Получить дневной прогресс своего персонажа за период или с limit"""
    telegram_id = int(payload.sub)
    try:
        character = await get_character_use_case.execute(telegram_id)

        if start_date and end_date:
            progress_list = await progress_repo.list_for_date_range(
                character.id, start_date, end_date
            )
        else:
            progress_list = await use_case.execute(character.id, limit=limit)

        return [DailyProgressResponse.model_validate(p) for p in progress_list]
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get("/me/day", response_model=DailyProgressResponse)
@inject
async def get_my_daily_progress_for_day(
    day: datetime = Query(..., description="День для получения прогресса"),
    payload: TokenPayload = Depends(get_access_token_payload),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: GetDailyProgressForDayUseCase = Depends(
        Provide[ApplicationContainer.get_daily_progress_for_day_use_case]
    ),
):
    """Получить прогресс своего персонажа за конкретный день"""
    telegram_id = int(payload.sub)
    try:
        character = await get_character_use_case.execute(telegram_id)
        progress = await use_case.execute(character.id, day)
        return DailyProgressResponse.model_validate(progress)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
