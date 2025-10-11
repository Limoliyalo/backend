from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
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
    "",
    response_model=list[ItemBackgroundPositionResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_positions_for_item(
    item_id: UUID = Query(..., description="ID предмета"),
    background_id: UUID = Query(..., description="ID фона"),
    use_case: ListPositionsForItemUseCase = Depends(
        Provide[ApplicationContainer.list_positions_for_item_use_case]
    ),
):
    """Получить все позиции предмета на фоне"""
    positions = await use_case.execute(item_id, background_id)
    return [ItemBackgroundPositionResponse.model_validate(pos) for pos in positions]


@router.get(
    "/{position_id}",
    response_model=ItemBackgroundPositionResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_position(
    position_id: UUID,
    use_case: GetPositionUseCase = Depends(
        Provide[ApplicationContainer.get_position_use_case]
    ),
):
    """Получить позицию по ID"""
    try:
        position = await use_case.execute(position_id)
        return ItemBackgroundPositionResponse.model_validate(position)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "",
    response_model=ItemBackgroundPositionResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_position(
    data: ItemBackgroundPositionCreate,
    use_case: CreatePositionUseCase = Depends(
        Provide[ApplicationContainer.create_position_use_case]
    ),
):
    """Создать новую позицию предмета на фоне"""
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
    "/{position_id}",
    response_model=ItemBackgroundPositionResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_position(
    position_id: UUID,
    data: ItemBackgroundPositionUpdate,
    use_case: UpdatePositionUseCase = Depends(
        Provide[ApplicationContainer.update_position_use_case]
    ),
):
    """Обновить позицию"""
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


@router.delete("/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_position(
    position_id: UUID,
    use_case: DeletePositionUseCase = Depends(
        Provide[ApplicationContainer.delete_position_use_case]
    ),
):
    """Удалить позицию"""
    try:
        await use_case.execute(position_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
