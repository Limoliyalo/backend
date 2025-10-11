from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.container import ApplicationContainer
from src.core.auth import get_admin_user
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.item_categories import (
    ItemCategoryCreate,
    ItemCategoryResponse,
    ItemCategoryUpdate,
)
from src.use_cases.item_categories.manage_item_categories import (
    CreateItemCategoryInput,
    CreateItemCategoryUseCase,
    DeleteItemCategoryUseCase,
    GetItemCategoryUseCase,
    ListItemCategoriesUseCase,
    UpdateItemCategoryInput,
    UpdateItemCategoryUseCase,
)

router = APIRouter(prefix="/item-categories", tags=["Item Categories"])


@router.get(
    "/admin", response_model=list[ItemCategoryResponse], status_code=status.HTTP_200_OK
)
@inject
async def list_item_categories(
    _: int = Depends(get_admin_user),
    use_case: ListItemCategoriesUseCase = Depends(
        Provide[ApplicationContainer.list_item_categories_use_case]
    ),
):
    """Получить список всех категорий предметов (требуется админ-доступ)"""
    categories = await use_case.execute()
    return [ItemCategoryResponse.model_validate(cat) for cat in categories]


@router.get(
    "/admin/{category_id}",
    response_model=ItemCategoryResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_item_category(
    category_id: UUID,
    _: int = Depends(get_admin_user),
    use_case: GetItemCategoryUseCase = Depends(
        Provide[ApplicationContainer.get_item_category_use_case]
    ),
):
    """Получить категорию по ID (требуется админ-доступ)"""
    try:
        category = await use_case.execute(category_id)
        return ItemCategoryResponse.model_validate(category)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/admin", response_model=ItemCategoryResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_item_category(
    data: ItemCategoryCreate,
    _: int = Depends(get_admin_user),
    use_case: CreateItemCategoryUseCase = Depends(
        Provide[ApplicationContainer.create_item_category_use_case]
    ),
):
    """Создать новую категорию предметов (требуется админ-доступ)"""
    input_data = CreateItemCategoryInput(name=data.name)
    category = await use_case.execute(input_data)
    return ItemCategoryResponse.model_validate(category)


@router.put(
    "/admin/{category_id}",
    response_model=ItemCategoryResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_item_category(
    category_id: UUID,
    data: ItemCategoryUpdate,
    _: int = Depends(get_admin_user),
    use_case: UpdateItemCategoryUseCase = Depends(
        Provide[ApplicationContainer.update_item_category_use_case]
    ),
):
    """Обновить категорию (требуется админ-доступ)"""
    try:
        input_data = UpdateItemCategoryInput(category_id=category_id, name=data.name)
        category = await use_case.execute(input_data)
        return ItemCategoryResponse.model_validate(category)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/admin/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_item_category(
    category_id: UUID,
    _: int = Depends(get_admin_user),
    use_case: DeleteItemCategoryUseCase = Depends(
        Provide[ApplicationContainer.delete_item_category_use_case]
    ),
):
    """Удалить категорию (требуется админ-доступ)"""
    try:
        await use_case.execute(category_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
