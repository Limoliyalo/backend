from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.domain.exceptions import EntityNotFoundException
from src.adapters.repositories.exceptions import RepositoryError
from src.drivers.rest.exceptions import NotFoundException, BadRequestException
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

router = APIRouter(prefix="/backgrounds", tags=["Backgrounds"])


@router.get("/admin", response_model=list[BackgroundResponse])
@inject
async def list_backgrounds(
    _: int = Depends(admin_user_provider),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    use_case: ListBackgroundsUseCase = Depends(
        Provide[ApplicationContainer.list_backgrounds_use_case]
    ),
):
    """Получить список всех фонов (требуется админ-доступ)"""
    try:
        backgrounds = await use_case.execute(limit=limit, offset=offset)
        return [BackgroundResponse.model_validate(bg) for bg in backgrounds]
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))


@router.get("/{background_id}/admin", response_model=BackgroundResponse)
@inject
async def get_background(
    background_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: GetBackgroundUseCase = Depends(
        Provide[ApplicationContainer.get_background_use_case]
    ),
):
    """Получить фон по ID (требуется админ-доступ)"""
    try:
        background = await use_case.execute(background_id)
        return BackgroundResponse.model_validate(background)
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/admin", response_model=BackgroundResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_background(
    data: BackgroundCreate,
    _: int = Depends(admin_user_provider),
    use_case: CreateBackgroundUseCase = Depends(
        Provide[ApplicationContainer.create_background_use_case]
    ),
):
    """Создать новый фон (требуется админ-доступ)"""
    input_data = CreateBackgroundInput(
        name=data.name,
        description=data.description,
        color=data.color,
        cost=data.cost,
        required_level=data.required_level,
        is_available=data.is_available,
    )
    try:
        background = await use_case.execute(input_data)
        return BackgroundResponse.model_validate(background)
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))


@router.patch("/{background_id}/admin", response_model=BackgroundResponse)
@inject
async def update_background(
    background_id: UUID,
    data: BackgroundUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdateBackgroundUseCase = Depends(
        Provide[ApplicationContainer.update_background_use_case]
    ),
):
    """Обновить фон (требуется админ-доступ)"""
    try:
        input_data = UpdateBackgroundInput(
            background_id=background_id,
            name=data.name,
            description=data.description,
            color=data.color,
            cost=data.cost,
            required_level=data.required_level,
            is_available=data.is_available,
        )
        background = await use_case.execute(input_data)
        return BackgroundResponse.model_validate(background)
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{background_id}/admin", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_background(
    background_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: DeleteBackgroundUseCase = Depends(
        Provide[ApplicationContainer.delete_background_use_case]
    ),
):
    """Удалить фон (требуется админ-доступ)"""
    try:
        await use_case.execute(background_id)
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get("/catalog", response_model=list[BackgroundResponse])
@inject
async def list_backgrounds_catalog(
    use_case: ListAvailableBackgroundsUseCase = Depends(
        Provide[ApplicationContainer.list_available_backgrounds_use_case]
    ),
):
    """Получить каталог доступных фонов (открытый endpoint)"""
    try:
        backgrounds = await use_case.execute()
        return [BackgroundResponse.model_validate(bg) for bg in backgrounds]
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))
