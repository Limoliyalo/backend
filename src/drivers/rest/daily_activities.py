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
from src.drivers.rest.exceptions import BadRequestException, NotFoundException
from src.drivers.rest.schemas.activities import (
    DailyActivityCreate,
    DailyActivityResponse,
    DailyActivityUpdate,
)
from src.ports.repositories.healthity.activities import DailyActivitiesRepository
from src.use_cases.characters.get_character import GetCharacterByUserUseCase
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
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get("/{activity_id}/admin", response_model=DailyActivityResponse)
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
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))
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
    try:
        activity = await use_case.execute(input_data)
        return DailyActivityResponse.model_validate(activity)
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))


@router.patch("/{activity_id}/admin", response_model=DailyActivityResponse)
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
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{activity_id}/admin", status_code=status.HTTP_204_NO_CONTENT)
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
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get("/me", response_model=list[DailyActivityResponse])
@inject
async def list_my_daily_activities(
    day: datetime | None = Query(
        None,
        description="День для получения активностей (используется если не указан диапазон)",
    ),
    start_date: datetime | None = Query(None, description="Начальная дата диапазона"),
    end_date: datetime | None = Query(None, description="Конечная дата диапазона"),
    payload: TokenPayload = Depends(get_access_token_payload),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: ListDailyActivitiesForDayUseCase = Depends(
        Provide[ApplicationContainer.list_daily_activities_for_day_use_case]
    ),
    activities_repo: DailyActivitiesRepository = Depends(
        Provide[ApplicationContainer.daily_activities_repository]
    ),
):
    """Получить активности текущего пользователя за день или диапазон дат"""
    telegram_id = int(payload.sub)
    try:

        character = await get_character_use_case.execute(telegram_id)

        if start_date and end_date:
            activities = await activities_repo.list_for_date_range(
                character.id, start_date, end_date
            )
        elif day:
            activities = await use_case.execute(character.id, day)
        else:
            raise BadRequestException(
                detail="Укажите либо day, либо start_date и end_date"
            )

        return [DailyActivityResponse.model_validate(a) for a in activities]
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/me", response_model=DailyActivityResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_my_daily_activity(
    activity_type_id: UUID = Query(..., description="ID типа активности"),
    date: datetime = Query(..., description="Дата активности"),
    value: int = Query(0, ge=0, description="Значение активности"),
    goal: int = Query(1, ge=1, description="Цель активности"),
    notes: str | None = Query(None, description="Заметки"),
    payload: TokenPayload = Depends(get_access_token_payload),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: CreateDailyActivityUseCase = Depends(
        Provide[ApplicationContainer.create_daily_activity_use_case]
    ),
):
    """Создать активность для текущего пользователя"""
    telegram_id = int(payload.sub)
    try:

        character = await get_character_use_case.execute(telegram_id)

        input_data = CreateDailyActivityInput(
            character_id=character.id,
            activity_type_id=activity_type_id,
            date=date,
            value=value,
            goal=goal,
            notes=notes,
        )
        activity = await use_case.execute(input_data)
        return DailyActivityResponse.model_validate(activity)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))


@router.patch("/{activity_id}/me", response_model=DailyActivityResponse)
@inject
async def update_my_daily_activity(
    activity_id: UUID,
    data: DailyActivityUpdate,
    payload: TokenPayload = Depends(get_access_token_payload),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    get_activity_use_case: GetDailyActivityUseCase = Depends(
        Provide[ApplicationContainer.get_daily_activity_use_case]
    ),
    update_use_case: UpdateDailyActivityUseCase = Depends(
        Provide[ApplicationContainer.update_daily_activity_use_case]
    ),
):
    """Обновить активность текущего пользователя"""
    telegram_id = int(payload.sub)
    try:

        character = await get_character_use_case.execute(telegram_id)

        activity = await get_activity_use_case.execute(activity_id)
        if activity.character_id != character.id:
            raise BadRequestException(detail="You can only update your own activities")

        input_data = UpdateDailyActivityInput(
            activity_id=activity_id,
            value=data.value,
            goal=data.goal,
            notes=data.notes,
        )
        updated_activity = await update_use_case.execute(input_data)
        return DailyActivityResponse.model_validate(updated_activity)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))
