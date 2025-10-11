from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.container import ApplicationContainer
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.character_items import (
    CharacterItemPurchase,
    CharacterItemResponse,
)
from src.use_cases.character_items.manage_character_items import (
    EquipItemUseCase,
    ListCharacterItemsUseCase,
    PurchaseItemInput,
    PurchaseItemUseCase,
    RemoveCharacterItemUseCase,
    UnequipItemUseCase,
)

router = APIRouter(prefix="/character-items", tags=["Character Items"])


@router.get(
    "/character/{character_id}",
    response_model=list[CharacterItemResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_character_items(
    character_id: UUID,
    use_case: ListCharacterItemsUseCase = Depends(
        Provide[ApplicationContainer.list_character_items_use_case]
    ),
):
    """Получить все предметы персонажа"""
    items = await use_case.execute(character_id)
    return [CharacterItemResponse.model_validate(item) for item in items]


@router.post(
    "/character/{character_id}",
    response_model=CharacterItemResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def purchase_item(
    character_id: UUID,
    data: CharacterItemPurchase,
    use_case: PurchaseItemUseCase = Depends(
        Provide[ApplicationContainer.purchase_item_use_case]
    ),
):
    """Купить предмет для персонажа"""
    input_data = PurchaseItemInput(
        character_id=character_id,
        item_id=data.item_id,
        is_equipped=data.is_equipped,
    )
    item = await use_case.execute(input_data)
    return CharacterItemResponse.model_validate(item)


@router.put(
    "/{character_item_id}/equip",
    response_model=CharacterItemResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def equip_item(
    character_item_id: UUID,
    use_case: EquipItemUseCase = Depends(
        Provide[ApplicationContainer.equip_item_use_case]
    ),
):
    """Надеть предмет"""
    try:
        item = await use_case.execute(character_item_id)
        return CharacterItemResponse.model_validate(item)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.put(
    "/{character_item_id}/unequip",
    response_model=CharacterItemResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def unequip_item(
    character_item_id: UUID,
    use_case: UnequipItemUseCase = Depends(
        Provide[ApplicationContainer.unequip_item_use_case]
    ),
):
    """Снять предмет"""
    try:
        item = await use_case.execute(character_item_id)
        return CharacterItemResponse.model_validate(item)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{character_item_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def remove_character_item(
    character_item_id: UUID,
    use_case: RemoveCharacterItemUseCase = Depends(
        Provide[ApplicationContainer.remove_character_item_use_case]
    ),
):
    """Удалить предмет у персонажа"""
    try:
        await use_case.execute(character_item_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
