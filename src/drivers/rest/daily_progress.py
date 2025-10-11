from datetime import datetime
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth import get_admin_user
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.activities import (
    DailyProgressCreate,
    DailyProgressResponse,
    DailyProgressUpdate,
)
from src.use_cases.daily_progress.manage_daily_progress import (
    CreateDailyProgressInput,
    CreateDailyProgressUseCase,
    DeleteDailyProgressUseCase,
    GetDailyProgressForDayUseCase,
    GetDailyProgressUseCase,
    ListDailyProgressForCharacterUseCase,
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
    _: int = Depends(get_admin_user),
    use_case: ListDailyProgressForCharacterUseCase = Depends(
        Provide[ApplicationContainer.list_daily_progress_for_character_use_case]
    ),
):
    """Получить весь прогресс персонажа (требуется админ-доступ)"""
    progress_list = await use_case.execute(character_id)
    return [DailyProgressResponse.model_validate(p) for p in progress_list]


@router.get(
    "/character/{character_id}/day",
    response_model=DailyProgressResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_daily_progress_for_day(
    character_id: UUID,
    day: datetime = Query(..., description="День для получения прогресса"),
    _: int = Depends(get_admin_user),
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


@router.get("/admin/{progress_id}", response_model=DailyProgressResponse)
@inject
async def get_daily_progress(
    progress_id: UUID,
    _: int = Depends(get_admin_user),
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
    _: int = Depends(get_admin_user),
    use_case: CreateDailyProgressUseCase = Depends(
        Provide[ApplicationContainer.create_daily_progress_use_case]
    ),
):
    """Создать или обновить дневной прогресс (требуется админ-доступ)"""
    input_data = CreateDailyProgressInput(
        character_id=data.character_id,
        date=data.date,
        experience_gained=data.experience_gained,
        level_at_end=data.level_at_end,
        mood_average=data.mood_average,
        behavior_index=data.behavior_index,
    )
    progress = await use_case.execute(input_data)
    return DailyProgressResponse.model_validate(progress)


@router.patch("/admin/{progress_id}", response_model=DailyProgressResponse)
@inject
async def update_daily_progress(
    progress_id: UUID,
    data: DailyProgressUpdate,
    _: int = Depends(get_admin_user),
    use_case: UpdateDailyProgressUseCase = Depends(
        Provide[ApplicationContainer.update_daily_progress_use_case]
    ),
):
    """Обновить дневной прогресс (требуется админ-доступ)"""
    try:
        input_data = UpdateDailyProgressInput(
            progress_id=progress_id,
            experience_gained=data.experience_gained,
            level_at_end=data.level_at_end,
            mood_average=data.mood_average,
            behavior_index=data.behavior_index,
        )
        progress = await use_case.execute(input_data)
        return DailyProgressResponse.model_validate(progress)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/admin/{progress_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_daily_progress(
    progress_id: UUID,
    _: int = Depends(get_admin_user),
    use_case: DeleteDailyProgressUseCase = Depends(
        Provide[ApplicationContainer.delete_daily_progress_use_case]
    ),
):
    """Удалить дневной прогресс (требуется админ-доступ)"""
    try:
        await use_case.execute(progress_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
