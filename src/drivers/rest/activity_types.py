from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.activities import (
    ActivityTypeCreate,
    ActivityTypeResponse,
    ActivityTypeUpdate,
)
from src.use_cases.activity_types.manage_activity_types import (
    CreateActivityTypeInput,
    CreateActivityTypeUseCase,
    DeleteActivityTypeUseCase,
    GetActivityTypeUseCase,
    ListActivityTypesUseCase,
    UpdateActivityTypeInput,
    UpdateActivityTypeUseCase,
)

router = APIRouter(prefix="/activity-types", tags=["Activity Types"])


@router.get(
    "/admin", response_model=list[ActivityTypeResponse], status_code=status.HTTP_200_OK
)
@inject
async def list_activity_types(
    _: int = Depends(admin_user_provider),
    use_case: ListActivityTypesUseCase = Depends(
        Provide[ApplicationContainer.list_activity_types_use_case]
    ),
):
    """Получить список всех типов активностей (требуется админ-доступ)"""
    activity_types = await use_case.execute()
    return [ActivityTypeResponse.model_validate(at) for at in activity_types]


@router.get(
    "/{activity_type_id}/admin",
    response_model=ActivityTypeResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_activity_type(
    activity_type_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: GetActivityTypeUseCase = Depends(
        Provide[ApplicationContainer.get_activity_type_use_case]
    ),
):
    """Получить тип активности по ID (требуется админ-доступ)"""
    try:
        activity_type = await use_case.execute(activity_type_id)
        return ActivityTypeResponse.model_validate(activity_type)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/admin", response_model=ActivityTypeResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_activity_type(
    data: ActivityTypeCreate,
    _: int = Depends(admin_user_provider),
    use_case: CreateActivityTypeUseCase = Depends(
        Provide[ApplicationContainer.create_activity_type_use_case]
    ),
):
    """Создать новый тип активности (требуется админ-доступ)"""
    input_data = CreateActivityTypeInput(
        name=data.name,
        unit=data.unit,
        color=data.color,
        daily_goal_default=data.daily_goal_default,
    )
    activity_type = await use_case.execute(input_data)
    return ActivityTypeResponse.model_validate(activity_type)


@router.patch(
    "/{activity_type_id}/admin",
    response_model=ActivityTypeResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_activity_type(
    activity_type_id: UUID,
    data: ActivityTypeUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdateActivityTypeUseCase = Depends(
        Provide[ApplicationContainer.update_activity_type_use_case]
    ),
):
    """Обновить тип активности (требуется админ-доступ)"""
    try:
        input_data = UpdateActivityTypeInput(
            activity_type_id=activity_type_id,
            name=data.name,
            unit=data.unit,
            color=data.color,
            daily_goal_default=data.daily_goal_default,
        )
        activity_type = await use_case.execute(input_data)
        return ActivityTypeResponse.model_validate(activity_type)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{activity_type_id}/admin", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_activity_type(
    activity_type_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: DeleteActivityTypeUseCase = Depends(
        Provide[ApplicationContainer.delete_activity_type_use_case]
    ),
):
    """Удалить тип активности (требуется админ-доступ)"""
    try:
        await use_case.execute(activity_type_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get("/catalog", response_model=list[ActivityTypeResponse])
@inject
async def list_activity_types_catalog(
    use_case: ListActivityTypesUseCase = Depends(
        Provide[ApplicationContainer.list_activity_types_use_case]
    ),
):
    """Получить каталог типов активностей (открытый endpoint)"""
    activity_types = await use_case.execute()
    return [ActivityTypeResponse.model_validate(at) for at in activity_types]
