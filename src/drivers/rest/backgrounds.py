from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.catalog import (
    BackgroundCreate,
    BackgroundResponse,
    BackgroundUpdate,
)
from src.use_cases.backgrounds.manage_backgrounds import (
    CreateBackgroundInput,
    CreateBackgroundUseCase,
    DeleteBackgroundUseCase,
    GetBackgroundUseCase,
    ListAvailableBackgroundsUseCase,
    ListBackgroundsUseCase,
    UpdateBackgroundInput,
    UpdateBackgroundUseCase,
)

router = APIRouter(prefix="/backgrounds", tags=["backgrounds"])


@router.get("/", response_model=list[BackgroundResponse])
@inject
async def list_backgrounds(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    use_case: ListBackgroundsUseCase = Depends(
        Provide[ApplicationContainer.list_backgrounds_use_case]
    ),
):
    """Получить список всех фонов"""
    backgrounds = await use_case.execute(limit=limit, offset=offset)
    return [BackgroundResponse.model_validate(bg) for bg in backgrounds]


@router.get("/available", response_model=list[BackgroundResponse])
@inject
async def list_available_backgrounds(
    use_case: ListAvailableBackgroundsUseCase = Depends(
        Provide[ApplicationContainer.list_available_backgrounds_use_case]
    ),
):
    """Получить список доступных фонов"""
    backgrounds = await use_case.execute()
    return [BackgroundResponse.model_validate(bg) for bg in backgrounds]


@router.get("/{background_id}", response_model=BackgroundResponse)
@inject
async def get_background(
    background_id: UUID,
    use_case: GetBackgroundUseCase = Depends(
        Provide[ApplicationContainer.get_background_use_case]
    ),
):
    """Получить фон по ID"""
    try:
        background = await use_case.execute(background_id)
        return BackgroundResponse.model_validate(background)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/", response_model=BackgroundResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_background(
    data: BackgroundCreate,
    use_case: CreateBackgroundUseCase = Depends(
        Provide[ApplicationContainer.create_background_use_case]
    ),
):
    """Создать новый фон"""
    input_data = CreateBackgroundInput(
        name=data.name,
        description=data.description,
        cost=data.cost,
        required_level=data.required_level,
        is_available=data.is_available,
    )
    background = await use_case.execute(input_data)
    return BackgroundResponse.model_validate(background)


@router.patch("/{background_id}", response_model=BackgroundResponse)
@inject
async def update_background(
    background_id: UUID,
    data: BackgroundUpdate,
    use_case: UpdateBackgroundUseCase = Depends(
        Provide[ApplicationContainer.update_background_use_case]
    ),
):
    """Обновить фон"""
    try:
        input_data = UpdateBackgroundInput(
            background_id=background_id,
            name=data.name,
            description=data.description,
            cost=data.cost,
            required_level=data.required_level,
            is_available=data.is_available,
        )
        background = await use_case.execute(input_data)
        return BackgroundResponse.model_validate(background)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{background_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_background(
    background_id: UUID,
    use_case: DeleteBackgroundUseCase = Depends(
        Provide[ApplicationContainer.delete_background_use_case]
    ),
):
    """Удалить фон"""
    try:
        await use_case.execute(background_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
