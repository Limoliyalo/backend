from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth import get_admin_user
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.character_backgrounds import (
    CharacterBackgroundPurchase,
    CharacterBackgroundResponse,
    CharacterBackgroundUpdate,
)
from src.use_cases.character_backgrounds.manage_character_backgrounds import (
    GetCharacterBackgroundUseCase,
    ListCharacterBackgroundsUseCase,
    PurchaseBackgroundInput,
    PurchaseBackgroundUseCase,
    RemoveCharacterBackgroundUseCase,
    UpdateCharacterBackgroundInput,
    UpdateCharacterBackgroundUseCase,
)

router = APIRouter(prefix="/character-backgrounds", tags=["Character Backgrounds"])


@router.get("/admin", response_model=list[CharacterBackgroundResponse])
@inject
async def list_character_backgrounds(
    character_id: UUID = Query(..., description="ID персонажа"),
    _: int = Depends(get_admin_user),
    use_case: ListCharacterBackgroundsUseCase = Depends(
        Provide[ApplicationContainer.list_character_backgrounds_use_case]
    ),
):
    """Получить список фонов персонажа (требуется админ-доступ)"""
    backgrounds = await use_case.execute(character_id)
    return [CharacterBackgroundResponse.model_validate(bg) for bg in backgrounds]


@router.get(
    "/admin/{character_background_id}", response_model=CharacterBackgroundResponse
)
@inject
async def get_character_background(
    character_background_id: UUID,
    _: int = Depends(get_admin_user),
    use_case: GetCharacterBackgroundUseCase = Depends(
        Provide[ApplicationContainer.get_character_background_use_case]
    ),
):
    """Получить фон персонажа по ID (требуется админ-доступ)"""
    try:
        background = await use_case.execute(character_background_id)
        return CharacterBackgroundResponse.model_validate(background)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/admin",
    response_model=CharacterBackgroundResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_character_background(
    data: CharacterBackgroundPurchase,
    _: int = Depends(get_admin_user),
    use_case: PurchaseBackgroundUseCase = Depends(
        Provide[ApplicationContainer.purchase_background_use_case]
    ),
):
    """Создать фон для персонажа (требуется админ-доступ)"""
    input_data = PurchaseBackgroundInput(
        character_id=data.character_id,
        background_id=data.background_id,
        is_active=data.is_active,
    )
    background = await use_case.execute(input_data)
    return CharacterBackgroundResponse.model_validate(background)


@router.patch(
    "/admin/{character_background_id}", response_model=CharacterBackgroundResponse
)
@inject
async def update_character_background(
    character_background_id: UUID,
    data: CharacterBackgroundUpdate,
    _: int = Depends(get_admin_user),
    use_case: UpdateCharacterBackgroundUseCase = Depends(
        Provide[ApplicationContainer.update_character_background_use_case]
    ),
):
    """Обновить фон персонажа (требуется админ-доступ)"""
    try:
        input_data = UpdateCharacterBackgroundInput(
            character_background_id=character_background_id,
            is_active=data.is_active,
        )
        background = await use_case.execute(input_data)
        return CharacterBackgroundResponse.model_validate(background)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete(
    "/admin/{character_background_id}", status_code=status.HTTP_204_NO_CONTENT
)
@inject
async def delete_character_background(
    character_background_id: UUID,
    _: int = Depends(get_admin_user),
    use_case: RemoveCharacterBackgroundUseCase = Depends(
        Provide[ApplicationContainer.remove_character_background_use_case]
    ),
):
    """Удалить фон персонажа (требуется админ-доступ)"""
    try:
        await use_case.execute(character_background_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
