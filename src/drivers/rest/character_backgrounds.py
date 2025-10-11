from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.container import ApplicationContainer
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.character_backgrounds import (
    CharacterBackgroundPurchase,
    CharacterBackgroundResponse,
)
from src.use_cases.character_backgrounds.manage_character_backgrounds import (
    ActivateBackgroundUseCase,
    DeactivateBackgroundUseCase,
    ListCharacterBackgroundsUseCase,
    PurchaseBackgroundInput,
    PurchaseBackgroundUseCase,
    RemoveCharacterBackgroundUseCase,
)

router = APIRouter(prefix="/character-backgrounds", tags=["Character Backgrounds"])


@router.get(
    "/character/{character_id}",
    response_model=list[CharacterBackgroundResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_character_backgrounds(
    character_id: UUID,
    use_case: ListCharacterBackgroundsUseCase = Depends(
        Provide[ApplicationContainer.list_character_backgrounds_use_case]
    ),
):
    """Получить все фоны персонажа"""
    backgrounds = await use_case.execute(character_id)
    return [CharacterBackgroundResponse.model_validate(bg) for bg in backgrounds]


@router.post(
    "/character/{character_id}",
    response_model=CharacterBackgroundResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def purchase_background(
    character_id: UUID,
    data: CharacterBackgroundPurchase,
    use_case: PurchaseBackgroundUseCase = Depends(
        Provide[ApplicationContainer.purchase_background_use_case]
    ),
):
    """Купить фон для персонажа"""
    input_data = PurchaseBackgroundInput(
        character_id=character_id,
        background_id=data.background_id,
        is_active=data.is_active,
    )
    background = await use_case.execute(input_data)
    return CharacterBackgroundResponse.model_validate(background)


@router.put(
    "/{character_background_id}/activate",
    response_model=CharacterBackgroundResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def activate_background(
    character_background_id: UUID,
    use_case: ActivateBackgroundUseCase = Depends(
        Provide[ApplicationContainer.activate_background_use_case]
    ),
):
    """Активировать фон"""
    try:
        background = await use_case.execute(character_background_id)
        return CharacterBackgroundResponse.model_validate(background)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.put(
    "/{character_background_id}/deactivate",
    response_model=CharacterBackgroundResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def deactivate_background(
    character_background_id: UUID,
    use_case: DeactivateBackgroundUseCase = Depends(
        Provide[ApplicationContainer.deactivate_background_use_case]
    ),
):
    """Деактивировать фон"""
    try:
        background = await use_case.execute(character_background_id)
        return CharacterBackgroundResponse.model_validate(background)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{character_background_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def remove_character_background(
    character_background_id: UUID,
    use_case: RemoveCharacterBackgroundUseCase = Depends(
        Provide[ApplicationContainer.remove_character_background_use_case]
    ),
):
    """Удалить фон у персонажа"""
    try:
        await use_case.execute(character_background_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
