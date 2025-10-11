from datetime import datetime
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.activities import (
    DailyActivityCreate,
    DailyActivityResponse,
)
from src.use_cases.daily_activities.manage_daily_activities import (
    CreateDailyActivityInput,
    CreateDailyActivityUseCase,
    ListDailyActivitiesForDayUseCase,
)

router = APIRouter(prefix="/daily-activities", tags=["Daily Activities"])


@router.post(
    "", response_model=DailyActivityResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_daily_activity(
    data: DailyActivityCreate,
    use_case: CreateDailyActivityUseCase = Depends(
        Provide[ApplicationContainer.create_daily_activity_use_case]
    ),
):
    """Создать или обновить дневную активность"""
    input_data = CreateDailyActivityInput(
        character_id=data.character_id,
        activity_type_id=data.activity_type_id,
        date=data.date,
        value=data.value,
        goal=data.goal,
        notes=data.notes,
    )
    activity = await use_case.execute(input_data)
    return DailyActivityResponse.model_validate(activity)


@router.get(
    "/character/{character_id}",
    response_model=list[DailyActivityResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_daily_activities_for_day(
    character_id: UUID,
    day: datetime = Query(..., description="День для получения активностей"),
    use_case: ListDailyActivitiesForDayUseCase = Depends(
        Provide[ApplicationContainer.list_daily_activities_for_day_use_case]
    ),
):
    """Получить все активности персонажа за конкретный день"""
    try:
        activities = await use_case.execute(character_id, day)
        return [DailyActivityResponse.model_validate(a) for a in activities]
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
