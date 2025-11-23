from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.core.auth.dependencies import get_telegram_current_user
from src.domain.exceptions import EntityNotFoundException
from src.adapters.repositories.exceptions import (
    RepositoryError,
    IntegrityConstraintError,
)
from src.drivers.rest.exceptions import NotFoundException, BadRequestException
from src.drivers.rest.schemas.catalog import (
    ItemCreate,
    ItemDelete,
    ItemResponse,
    ItemUpdate,
)
from src.drivers.rest.schemas.character_items import (
    CharacterItemResponse,
    CharacterItemUserPurchase,
)
from src.use_cases.character_items.manage_character_items import (
    ToggleFavoriteItemInput,
    ToggleFavoriteItemUseCase,
)
from src.use_cases.characters.get_character import GetCharacterByUserUseCase
from src.use_cases.items.manage_items import (
    CreateItemInput,
    CreateItemUseCase,
    DeleteItemUseCase,
    GetItemUseCase,
    ListAvailableItemsUseCase,
    ListItemsUseCase,
    UpdateItemInput,
    UpdateItemUseCase,
)

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/admin", response_model=list[ItemResponse])
@inject
async def list_items(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _: int = Depends(admin_user_provider),
    use_case: ListItemsUseCase = Depends(
        Provide[ApplicationContainer.list_items_use_case]
    ),
):
    """Получить список всех предметов (требуется админ-доступ)"""
    try:
        items = await use_case.execute(limit=limit, offset=offset)
        return [ItemResponse.model_validate(item) for item in items]
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))


@router.get("/{item_id}/admin", response_model=ItemResponse)
@inject
async def get_item(
    item_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: GetItemUseCase = Depends(Provide[ApplicationContainer.get_item_use_case]),
):
    """Получить предмет по ID (требуется админ-доступ)"""
    try:
        item = await use_case.execute(item_id)
        return ItemResponse.model_validate(item)
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post("/admin", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_item(
    data: ItemCreate,
    _: int = Depends(admin_user_provider),
    use_case: CreateItemUseCase = Depends(
        Provide[ApplicationContainer.create_item_use_case]
    ),
):
    """Создать новый предмет (требуется админ-доступ)"""
    input_data = CreateItemInput(
        category_id=data.category_id,
        name=data.name,
        description=data.description,
        cost=data.cost,
        required_level=data.required_level,
        is_available=data.is_available,
        picture_url=data.picture_url,
    )
    try:
        item = await use_case.execute(input_data)
        return ItemResponse.model_validate(item)
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))


@router.patch("/admin", response_model=ItemResponse)
@inject
async def update_item(
    data: ItemUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdateItemUseCase = Depends(
        Provide[ApplicationContainer.update_item_use_case]
    ),
):
    """Обновить предмет (требуется админ-доступ)"""
    try:
        input_data = UpdateItemInput(
            item_id=data.item_id,
            name=data.name,
            description=data.description,
            cost=data.cost,
            required_level=data.required_level,
            is_available=data.is_available,
            picture_url=data.picture_url,
        )
        item = await use_case.execute(input_data)
        return ItemResponse.model_validate(item)
    except IntegrityConstraintError as e:
        raise BadRequestException(detail=str(e))
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/admin", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_item(
    data: ItemDelete,
    _: int = Depends(admin_user_provider),
    use_case: DeleteItemUseCase = Depends(
        Provide[ApplicationContainer.delete_item_use_case]
    ),
):
    """Удалить предмет (требуется админ-доступ)"""
    try:
        await use_case.execute(data.item_id)
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get("/catalog", response_model=list[ItemResponse])
@inject
async def list_items_catalog(
    use_case: ListAvailableItemsUseCase = Depends(
        Provide[ApplicationContainer.list_available_items_use_case]
    ),
):
    """Получить каталог доступных предметов (открытый endpoint)"""
    try:
        items = await use_case.execute()
        return [ItemResponse.model_validate(item) for item in items]
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))


@router.post("/me/toggle-favorite", response_model=CharacterItemResponse)
@inject
async def toggle_favorite_item(
    item_data: CharacterItemUserPurchase,
    telegram_id: int = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: ToggleFavoriteItemUseCase = Depends(
        Provide[ApplicationContainer.toggle_favorite_item_use_case]
    ),
):
    """Переключить избранное для предмета (создает запись если её нет)"""

    try:
        character = await get_character_use_case.execute(telegram_id)

        input_data = ToggleFavoriteItemInput(
            character_id=character.id,
            item_id=item_data.item_id,
        )
        updated_item = await use_case.execute(input_data)
        return CharacterItemResponse.model_validate(updated_item)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))
