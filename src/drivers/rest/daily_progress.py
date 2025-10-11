from datetime import datetime
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.activities import (
    DailyProgressCreate,
    DailyProgressResponse,
)
from src.use_cases.daily_progress.manage_daily_progress import (
    CreateDailyProgressInput,
    CreateDailyProgressUseCase,
    GetDailyProgressForDayUseCase,
)

router = APIRouter(prefix="/daily-progress", tags=["Daily Progress"])


@router.post(
    "", response_model=DailyProgressResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_daily_progress(
    data: DailyProgressCreate,
    use_case: CreateDailyProgressUseCase = Depends(
        Provide[ApplicationContainer.create_daily_progress_use_case]
    ),
):
    """Создать или обновить дневной прогресс"""
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


@router.get(
    "/character/{character_id}",
    response_model=DailyProgressResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_daily_progress_for_day(
    character_id: UUID,
    day: datetime = Query(..., description="День для получения прогресса"),
    use_case: GetDailyProgressForDayUseCase = Depends(
        Provide[ApplicationContainer.get_daily_progress_for_day_use_case]
    ),
):
    """Получить прогресс персонажа за конкретный день"""
    try:
        progress = await use_case.execute(character_id, day)
        return DailyProgressResponse.model_validate(progress)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
