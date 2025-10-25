from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.core.auth.dependencies import get_telegram_current_user
from src.domain.value_objects.telegram_id import TelegramId
from src.domain.exceptions import EntityNotFoundException
from src.adapters.repositories.exceptions import RepositoryError
from src.drivers.rest.exceptions import NotFoundException, BadRequestException
from src.drivers.rest.schemas.character_items import (
    CharacterItemPurchase,
    CharacterItemResponse,
    CharacterItemUpdate,
)
from src.use_cases.character_items.manage_character_items import (
    EquipItemUseCase,
    GetCharacterItemUseCase,
    ListCharacterItemsUseCase,
    PurchaseItemInput,
    PurchaseItemUseCase,
    PurchaseItemWithBalanceInput,
    PurchaseItemWithBalanceUseCase,
    RemoveCharacterItemUseCase,
    ToggleFavouriteItemUseCase,
    UnequipItemUseCase,
    UpdateCharacterItemInput,
    UpdateCharacterItemUseCase,
)
from src.use_cases.characters.get_character import GetCharacterByUserUseCase

router = APIRouter(prefix="/character-items", tags=["Character Items"])


@router.get("/admin", response_model=list[CharacterItemResponse])
@inject
async def list_character_items(
    character_id: UUID = Query(..., description="ID персонажа"),
    _: int = Depends(admin_user_provider),
    use_case: ListCharacterItemsUseCase = Depends(
        Provide[ApplicationContainer.list_character_items_use_case]
    ),
):
    """Получить список предметов персонажа (требуется админ-доступ)"""
    try:
        items = await use_case.execute(character_id)
        return [CharacterItemResponse.model_validate(item) for item in items]
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))


@router.get("/{character_item_id}/admin", response_model=CharacterItemResponse)
@inject
async def get_character_item(
    character_item_id: UUID,
    _: int = Depends(admin_user_provider),
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
    _: int = Depends(admin_user_provider),
    use_case: PurchaseItemUseCase = Depends(
        Provide[ApplicationContainer.purchase_item_use_case]
    ),
):
    """Создать предмет для персонажа (требуется админ-доступ)"""
    input_data = PurchaseItemInput(
        character_id=data.character_id,
        item_id=data.item_id,
        is_active=data.is_active,
        is_favorite=data.is_favorite,
    )
    item = await use_case.execute(input_data)
    return CharacterItemResponse.model_validate(item)


@router.patch("/{character_item_id}/admin", response_model=CharacterItemResponse)
@inject
async def update_character_item(
    character_item_id: UUID,
    data: CharacterItemUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdateCharacterItemUseCase = Depends(
        Provide[ApplicationContainer.update_character_item_use_case]
    ),
):
    """Обновить предмет персонажа (требуется админ-доступ)"""
    try:
        input_data = UpdateCharacterItemInput(
            character_item_id=character_item_id,
            is_active=data.is_active,
            is_favorite=data.is_favorite,
        )
        item = await use_case.execute(input_data)
        return CharacterItemResponse.model_validate(item)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{character_item_id}/admin", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_character_item(
    character_item_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: RemoveCharacterItemUseCase = Depends(
        Provide[ApplicationContainer.remove_character_item_use_case]
    ),
):
    """Удалить предмет персонажа (требуется админ-доступ)"""
    try:
        await use_case.execute(character_item_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.patch("/me/{character_item_id}/equip", response_model=CharacterItemResponse)
@inject
async def equip_my_item(
    character_item_id: UUID,
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    get_item_use_case: GetCharacterItemUseCase = Depends(
        Provide[ApplicationContainer.get_character_item_use_case]
    ),
    use_case: EquipItemUseCase = Depends(
        Provide[ApplicationContainer.equip_item_use_case]
    ),
):
    """Активировать предмет"""

    try:
        character = await get_character_use_case.execute(telegram_id.value)
        item = await get_item_use_case.execute(character_item_id)

        if item.character_id != character.id:
            raise NotFoundException(detail="Item does not belong to your character")

        updated_item = await use_case.execute(character_item_id)
        return CharacterItemResponse.model_validate(updated_item)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.patch("/me/{character_item_id}/unequip", response_model=CharacterItemResponse)
@inject
async def unequip_my_item(
    character_item_id: UUID,
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    get_item_use_case: GetCharacterItemUseCase = Depends(
        Provide[ApplicationContainer.get_character_item_use_case]
    ),
    use_case: UnequipItemUseCase = Depends(
        Provide[ApplicationContainer.unequip_item_use_case]
    ),
):
    """Деактивировать предмет"""

    try:
        character = await get_character_use_case.execute(telegram_id.value)
        item = await get_item_use_case.execute(character_item_id)

        if item.character_id != character.id:
            raise NotFoundException(detail="Item does not belong to your character")

        updated_item = await use_case.execute(character_item_id)
        return CharacterItemResponse.model_validate(updated_item)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.patch("/me/{character_item_id}/favourite", response_model=CharacterItemResponse)
@inject
async def toggle_favourite_item(
    character_item_id: UUID,
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    get_item_use_case: GetCharacterItemUseCase = Depends(
        Provide[ApplicationContainer.get_character_item_use_case]
    ),
    use_case: ToggleFavouriteItemUseCase = Depends(
        Provide[ApplicationContainer.toggle_favourite_item_use_case]
    ),
):
    """Добавить/убрать предмет из избранного"""

    try:
        character = await get_character_use_case.execute(telegram_id.value)
        item = await get_item_use_case.execute(character_item_id)

        if item.character_id != character.id:
            raise NotFoundException(detail="Item does not belong to your character")

        updated_item = await use_case.execute(character_item_id)
        return CharacterItemResponse.model_validate(updated_item)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get("/me", response_model=list[CharacterItemResponse])
@inject
async def list_my_items(
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: ListCharacterItemsUseCase = Depends(
        Provide[ApplicationContainer.list_character_items_use_case]
    ),
):
    """Получить список купленных предметов текущего пользователя"""

    try:
        character = await get_character_use_case.execute(telegram_id.value)
        items = await use_case.execute(character.id)
        return [CharacterItemResponse.model_validate(item) for item in items]
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/me/purchase",
    response_model=CharacterItemResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def purchase_item(
    item_id: UUID = Query(..., description="ID предмета для покупки"),
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: PurchaseItemWithBalanceUseCase = Depends(
        Provide[ApplicationContainer.purchase_item_with_balance_use_case]
    ),
):
    """Купить предмет (списываются монетки с баланса)"""

    try:
        character = await get_character_use_case.execute(telegram_id.value)

        input_data = PurchaseItemWithBalanceInput(
            user_tg_id=telegram_id.value,
            character_id=character.id,
            item_id=item_id,
        )
        purchased_item = await use_case.execute(input_data)
        return CharacterItemResponse.model_validate(purchased_item)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))
