from datetime import datetime
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.activities import (
    DailyActivityCreate,
    DailyActivityResponse,
    DailyActivityUpdate,
)
from src.use_cases.daily_activities.manage_daily_activities import (
    CreateDailyActivityInput,
    CreateDailyActivityUseCase,
    DeleteDailyActivityUseCase,
    GetDailyActivityUseCase,
    ListDailyActivitiesForDayUseCase,
    UpdateDailyActivityInput,
    UpdateDailyActivityUseCase,
)

router = APIRouter(prefix="/daily-activities", tags=["Daily Activities"])


@router.get(
    "/character/{character_id}",
    response_model=list[DailyActivityResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_daily_activities_for_day(
    character_id: UUID,
    day: datetime = Query(..., description="День для получения активностей"),
    _: int = Depends(admin_user_provider),
    use_case: ListDailyActivitiesForDayUseCase = Depends(
        Provide[ApplicationContainer.list_daily_activities_for_day_use_case]
    ),
):
    """Получить все активности персонажа за конкретный день (требуется админ-доступ)"""
    try:
        activities = await use_case.execute(character_id, day)
        return [DailyActivityResponse.model_validate(a) for a in activities]
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get("/admin/{activity_id}", response_model=DailyActivityResponse)
@inject
async def get_daily_activity(
    activity_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: GetDailyActivityUseCase = Depends(
        Provide[ApplicationContainer.get_daily_activity_use_case]
    ),
):
    """Получить дневную активность по ID (требуется админ-доступ)"""
    try:
        activity = await use_case.execute(activity_id)
        return DailyActivityResponse.model_validate(activity)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/admin", response_model=DailyActivityResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_daily_activity(
    data: DailyActivityCreate,
    _: int = Depends(admin_user_provider),
    use_case: CreateDailyActivityUseCase = Depends(
        Provide[ApplicationContainer.create_daily_activity_use_case]
    ),
):
    """Создать или обновить дневную активность (требуется админ-доступ)"""
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


@router.patch("/admin/{activity_id}", response_model=DailyActivityResponse)
@inject
async def update_daily_activity(
    activity_id: UUID,
    data: DailyActivityUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdateDailyActivityUseCase = Depends(
        Provide[ApplicationContainer.update_daily_activity_use_case]
    ),
):
    """Обновить дневную активность (требуется админ-доступ)"""
    try:
        input_data = UpdateDailyActivityInput(
            activity_id=activity_id,
            value=data.value,
            goal=data.goal,
            notes=data.notes,
        )
        activity = await use_case.execute(input_data)
        return DailyActivityResponse.model_validate(activity)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/admin/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_daily_activity(
    activity_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: DeleteDailyActivityUseCase = Depends(
        Provide[ApplicationContainer.delete_daily_activity_use_case]
    ),
):
    """Удалить дневную активность (требуется админ-доступ)"""
    try:
        await use_case.execute(activity_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
