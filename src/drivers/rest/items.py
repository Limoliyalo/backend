from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.catalog import ItemCreate, ItemResponse, ItemUpdate
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

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=list[ItemResponse])
@inject
async def list_items(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    use_case: ListItemsUseCase = Depends(
        Provide[ApplicationContainer.list_items_use_case]
    ),
):
    """Получить список всех предметов"""
    items = await use_case.execute(limit=limit, offset=offset)
    return [ItemResponse.model_validate(item) for item in items]


@router.get("/available", response_model=list[ItemResponse])
@inject
async def list_available_items(
    use_case: ListAvailableItemsUseCase = Depends(
        Provide[ApplicationContainer.list_available_items_use_case]
    ),
):
    """Получить список доступных предметов"""
    items = await use_case.execute()
    return [ItemResponse.model_validate(item) for item in items]


@router.get("/{item_id}", response_model=ItemResponse)
@inject
async def get_item(
    item_id: UUID,
    use_case: GetItemUseCase = Depends(Provide[ApplicationContainer.get_item_use_case]),
):
    """Получить предмет по ID"""
    try:
        item = await use_case.execute(item_id)
        return ItemResponse.model_validate(item)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_item(
    data: ItemCreate,
    use_case: CreateItemUseCase = Depends(
        Provide[ApplicationContainer.create_item_use_case]
    ),
):
    """Создать новый предмет"""
    input_data = CreateItemInput(
        category_id=data.category_id,
        name=data.name,
        description=data.description,
        cost=data.cost,
        required_level=data.required_level,
        is_available=data.is_available,
    )
    item = await use_case.execute(input_data)
    return ItemResponse.model_validate(item)


@router.patch("/{item_id}", response_model=ItemResponse)
@inject
async def update_item(
    item_id: UUID,
    data: ItemUpdate,
    use_case: UpdateItemUseCase = Depends(
        Provide[ApplicationContainer.update_item_use_case]
    ),
):
    """Обновить предмет"""
    try:
        input_data = UpdateItemInput(
            item_id=item_id,
            name=data.name,
            description=data.description,
            cost=data.cost,
            required_level=data.required_level,
            is_available=data.is_available,
        )
        item = await use_case.execute(input_data)
        return ItemResponse.model_validate(item)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_item(
    item_id: UUID,
    use_case: DeleteItemUseCase = Depends(
        Provide[ApplicationContainer.delete_item_use_case]
    ),
):
    """Удалить предмет"""
    try:
        await use_case.execute(item_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
