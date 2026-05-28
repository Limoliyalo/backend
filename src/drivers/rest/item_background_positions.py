from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.core.auth.dependencies import get_telegram_current_user
from src.domain.exceptions import EntityNotFoundException
from src.adapters.repositories.exceptions import RepositoryError
from src.drivers.rest.exceptions import NotFoundException, BadRequestException
from src.drivers.rest.schemas.item_background_positions import (
    ItemBackgroundPositionCreate,
    ItemBackgroundPositionDelete,
    ItemBackgroundPositionResponse,
    ItemBackgroundPositionUpdate,
    ItemWithPositionResponse,
)
from src.use_cases.item_background_positions.manage_positions import (
    CreatePositionInput,
    CreatePositionUseCase,
    DeletePositionUseCase,
    GetPositionByItemAndBackgroundUseCase,
    GetPositionUseCase,
    ListItemsWithPositionsForBackgroundUseCase,
    ListPositionsForItemUseCase,
    UpdatePositionInput,
    UpdatePositionUseCase,
)

router = APIRouter(
    prefix="/item-background-positions", tags=["Item Background Positions"]
)


@router.get(
    "/me/items",
    response_model=list[ItemWithPositionResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_items_with_positions_for_background(
    background_id: UUID = Query(..., description="ID фона"),
    _: int = Depends(get_telegram_current_user),
    use_case: ListItemsWithPositionsForBackgroundUseCase = Depends(
        Provide[ApplicationContainer.list_items_with_positions_for_background_use_case]
    ),
):
    """Получить все предметы с позициями для указанного фона"""
    pairs = await use_case.execute(background_id)
    return [
        ItemWithPositionResponse(
            item=item,
            position=ItemBackgroundPositionResponse.model_validate(position),
        )
        for item, position in pairs
    ]


@router.get(
    "/me",
    response_model=ItemBackgroundPositionResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_position_by_item_and_background(
    item_id: UUID = Query(..., description="ID предмета"),
    background_id: UUID = Query(..., description="ID фона"),
    _: int = Depends(get_telegram_current_user),
    use_case: GetPositionByItemAndBackgroundUseCase = Depends(
        Provide[ApplicationContainer.get_position_by_item_and_background_use_case]
    ),
):
    """Получить позицию предмета на фоне по item_id и background_id"""
    try:
        position = await use_case.execute(item_id, background_id)
        return ItemBackgroundPositionResponse.model_validate(position)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get(
    "/admin",
    response_model=list[ItemBackgroundPositionResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_positions_for_item(
    item_id: UUID = Query(..., description="ID предмета"),
    background_id: UUID = Query(..., description="ID фона"),
    _: int = Depends(admin_user_provider),
    use_case: ListPositionsForItemUseCase = Depends(
        Provide[ApplicationContainer.list_positions_for_item_use_case]
    ),
):
    """Получить все позиции предмета на фоне (требуется админ-доступ)"""
    try:
        positions = await use_case.execute(item_id, background_id)
        return [ItemBackgroundPositionResponse.model_validate(pos) for pos in positions]
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))


@router.get(
    "/{position_id}/admin",
    response_model=ItemBackgroundPositionResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_position(
    position_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: GetPositionUseCase = Depends(
        Provide[ApplicationContainer.get_position_use_case]
    ),
):
    """Получить позицию по ID (требуется админ-доступ)"""
    try:
        position = await use_case.execute(position_id)
        return ItemBackgroundPositionResponse.model_validate(position)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/admin",
    response_model=ItemBackgroundPositionResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_position(
    data: ItemBackgroundPositionCreate,
    _: int = Depends(admin_user_provider),
    use_case: CreatePositionUseCase = Depends(
        Provide[ApplicationContainer.create_position_use_case]
    ),
):
    """Создать новую позицию предмета на фоне (требуется админ-доступ)"""
    input_data = CreatePositionInput(
        item_id=data.item_id,
        background_id=data.background_id,
        position_x=data.position_x,
        position_y=data.position_y,
        position_z=data.position_z,
        size=data.size,
    )
    position = await use_case.execute(input_data)
    return ItemBackgroundPositionResponse.model_validate(position)


@router.put(
    "/admin",
    response_model=ItemBackgroundPositionResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_position(
    data: ItemBackgroundPositionUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdatePositionUseCase = Depends(
        Provide[ApplicationContainer.update_position_use_case]
    ),
):
    """Обновить позицию (требуется админ-доступ)"""
    try:
        input_data = UpdatePositionInput(
            position_id=data.position_id,
            position_x=data.position_x,
            position_y=data.position_y,
            position_z=data.position_z,
            size=data.size,
        )
        position = await use_case.execute(input_data)
        return ItemBackgroundPositionResponse.model_validate(position)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/admin", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_position(
    data: ItemBackgroundPositionDelete,
    _: int = Depends(admin_user_provider),
    use_case: DeletePositionUseCase = Depends(
        Provide[ApplicationContainer.delete_position_use_case]
    ),
):
    """Удалить позицию (требуется админ-доступ)"""
    try:
        await use_case.execute(data.position_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
