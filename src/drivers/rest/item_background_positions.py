from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth import get_admin_user
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.item_background_positions import (
    ItemBackgroundPositionCreate,
    ItemBackgroundPositionResponse,
    ItemBackgroundPositionUpdate,
)
from src.use_cases.item_background_positions.manage_positions import (
    CreatePositionInput,
    CreatePositionUseCase,
    DeletePositionUseCase,
    GetPositionUseCase,
    ListPositionsForItemUseCase,
    UpdatePositionInput,
    UpdatePositionUseCase,
)

router = APIRouter(
    prefix="/item-background-positions", tags=["Item Background Positions"]
)


@router.get(
    "/admin",
    response_model=list[ItemBackgroundPositionResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_positions_for_item(
    item_id: UUID = Query(..., description="ID предмета"),
    background_id: UUID = Query(..., description="ID фона"),
    _: int = Depends(get_admin_user),
    use_case: ListPositionsForItemUseCase = Depends(
        Provide[ApplicationContainer.list_positions_for_item_use_case]
    ),
):
    """Получить все позиции предмета на фоне (требуется админ-доступ)"""
    positions = await use_case.execute(item_id, background_id)
    return [ItemBackgroundPositionResponse.model_validate(pos) for pos in positions]


@router.get(
    "/admin/{position_id}",
    response_model=ItemBackgroundPositionResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_position(
    position_id: UUID,
    _: int = Depends(get_admin_user),
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
    _: int = Depends(get_admin_user),
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
    )
    position = await use_case.execute(input_data)
    return ItemBackgroundPositionResponse.model_validate(position)


@router.put(
    "/admin/{position_id}",
    response_model=ItemBackgroundPositionResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_position(
    position_id: UUID,
    data: ItemBackgroundPositionUpdate,
    _: int = Depends(get_admin_user),
    use_case: UpdatePositionUseCase = Depends(
        Provide[ApplicationContainer.update_position_use_case]
    ),
):
    """Обновить позицию (требуется админ-доступ)"""
    try:
        input_data = UpdatePositionInput(
            position_id=position_id,
            position_x=data.position_x,
            position_y=data.position_y,
            position_z=data.position_z,
        )
        position = await use_case.execute(input_data)
        return ItemBackgroundPositionResponse.model_validate(position)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/admin/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_position(
    position_id: UUID,
    _: int = Depends(get_admin_user),
    use_case: DeletePositionUseCase = Depends(
        Provide[ApplicationContainer.delete_position_use_case]
    ),
):
    """Удалить позицию (требуется админ-доступ)"""
    try:
        await use_case.execute(position_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
