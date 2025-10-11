from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth import get_admin_user
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.character_items import (
    CharacterItemPurchase,
    CharacterItemResponse,
    CharacterItemUpdate,
)
from src.use_cases.character_items.manage_character_items import (
    GetCharacterItemUseCase,
    ListCharacterItemsUseCase,
    PurchaseItemInput,
    PurchaseItemUseCase,
    RemoveCharacterItemUseCase,
    UpdateCharacterItemInput,
    UpdateCharacterItemUseCase,
)

router = APIRouter(prefix="/character-items", tags=["Character Items"])


@router.get("/admin", response_model=list[CharacterItemResponse])
@inject
async def list_character_items(
    character_id: UUID = Query(..., description="ID персонажа"),
    _: int = Depends(get_admin_user),
    use_case: ListCharacterItemsUseCase = Depends(
        Provide[ApplicationContainer.list_character_items_use_case]
    ),
):
    """Получить список предметов персонажа (требуется админ-доступ)"""
    items = await use_case.execute(character_id)
    return [CharacterItemResponse.model_validate(item) for item in items]


@router.get("/admin/{character_item_id}", response_model=CharacterItemResponse)
@inject
async def get_character_item(
    character_item_id: UUID,
    _: int = Depends(get_admin_user),
    use_case: GetCharacterItemUseCase = Depends(
        Provide[ApplicationContainer.get_character_item_use_case]
    ),
):
    """Получить предмет персонажа по ID (требуется админ-доступ)"""
    try:
        item = await use_case.execute(character_item_id)
        return CharacterItemResponse.model_validate(item)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/admin", response_model=CharacterItemResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_character_item(
    data: CharacterItemPurchase,
    _: int = Depends(get_admin_user),
    use_case: PurchaseItemUseCase = Depends(
        Provide[ApplicationContainer.purchase_item_use_case]
    ),
):
    """Создать предмет для персонажа (требуется админ-доступ)"""
    input_data = PurchaseItemInput(
        character_id=data.character_id,
        item_id=data.item_id,
        is_equipped=data.is_equipped,
    )
    item = await use_case.execute(input_data)
    return CharacterItemResponse.model_validate(item)


@router.patch("/admin/{character_item_id}", response_model=CharacterItemResponse)
@inject
async def update_character_item(
    character_item_id: UUID,
    data: CharacterItemUpdate,
    _: int = Depends(get_admin_user),
    use_case: UpdateCharacterItemUseCase = Depends(
        Provide[ApplicationContainer.update_character_item_use_case]
    ),
):
    """Обновить предмет персонажа (требуется админ-доступ)"""
    try:
        input_data = UpdateCharacterItemInput(
            character_item_id=character_item_id,
            is_equipped=data.is_equipped,
        )
        item = await use_case.execute(input_data)
        return CharacterItemResponse.model_validate(item)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/admin/{character_item_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_character_item(
    character_item_id: UUID,
    _: int = Depends(get_admin_user),
    use_case: RemoveCharacterItemUseCase = Depends(
        Provide[ApplicationContainer.remove_character_item_use_case]
    ),
):
    """Удалить предмет персонажа (требуется админ-доступ)"""
    try:
        await use_case.execute(character_item_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
