from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.container import ApplicationContainer
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.activities import (
    ActivityTypeCreate,
    ActivityTypeResponse,
)
from src.use_cases.activity_types.manage_activity_types import (
    CreateActivityTypeInput,
    CreateActivityTypeUseCase,
    GetActivityTypeByNameUseCase,
    ListActivityTypesUseCase,
)

router = APIRouter(prefix="/activity-types", tags=["Activity Types"])


@router.get(
    "", response_model=list[ActivityTypeResponse], status_code=status.HTTP_200_OK
)
@inject
async def list_activity_types(
    use_case: ListActivityTypesUseCase = Depends(
        Provide[ApplicationContainer.list_activity_types_use_case]
    ),
):
    """Получить список всех типов активностей"""
    activity_types = await use_case.execute()
    return [ActivityTypeResponse.model_validate(at) for at in activity_types]


@router.get(
    "/by-name/{name}",
    response_model=ActivityTypeResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_activity_type_by_name(
    name: str,
    use_case: GetActivityTypeByNameUseCase = Depends(
        Provide[ApplicationContainer.get_activity_type_by_name_use_case]
    ),
):
    """Получить тип активности по имени"""
    try:
        activity_type = await use_case.execute(name)
        return ActivityTypeResponse.model_validate(activity_type)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "", response_model=ActivityTypeResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_activity_type(
    data: ActivityTypeCreate,
    use_case: CreateActivityTypeUseCase = Depends(
        Provide[ApplicationContainer.create_activity_type_use_case]
    ),
):
    """Создать новый тип активности"""
    input_data = CreateActivityTypeInput(
        name=data.name,
        unit=data.unit,
        color=data.color,
        daily_goal_default=data.daily_goal_default,
    )
    activity_type = await use_case.execute(input_data)
    return ActivityTypeResponse.model_validate(activity_type)
