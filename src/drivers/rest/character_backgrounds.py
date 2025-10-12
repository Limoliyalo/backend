from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.core.auth.dependencies import get_access_token_payload
from src.core.auth.jwt_service import TokenPayload
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.character_backgrounds import (
    CharacterBackgroundPurchase,
    CharacterBackgroundResponse,
    CharacterBackgroundUpdate,
)
from src.use_cases.character_backgrounds.manage_character_backgrounds import (
    ActivateBackgroundUseCase,
    DeactivateBackgroundUseCase,
    GetCharacterBackgroundUseCase,
    ListCharacterBackgroundsUseCase,
    PurchaseBackgroundInput,
    PurchaseBackgroundUseCase,
    PurchaseBackgroundWithBalanceInput,
    PurchaseBackgroundWithBalanceUseCase,
    RemoveCharacterBackgroundUseCase,
    ToggleFavouriteBackgroundUseCase,
    UpdateCharacterBackgroundInput,
    UpdateCharacterBackgroundUseCase,
)
from src.use_cases.characters.get_character import GetCharacterByUserUseCase
from src.drivers.rest.exceptions import BadRequestException

router = APIRouter(prefix="/character-backgrounds", tags=["Character Backgrounds"])


@router.get("/admin", response_model=list[CharacterBackgroundResponse])
@inject
async def list_character_backgrounds(
    character_id: UUID = Query(..., description="ID персонажа"),
    _: int = Depends(admin_user_provider),
    use_case: ListCharacterBackgroundsUseCase = Depends(
        Provide[ApplicationContainer.list_character_backgrounds_use_case]
    ),
):
    """Получить список фонов персонажа (требуется админ-доступ)"""
    backgrounds = await use_case.execute(character_id)
    return [CharacterBackgroundResponse.model_validate(bg) for bg in backgrounds]


@router.get(
    "/{character_background_id}/admin", response_model=CharacterBackgroundResponse
)
@inject
async def get_character_background(
    character_background_id: UUID,
    _: int = Depends(admin_user_provider),
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
    _: int = Depends(admin_user_provider),
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
    "/{character_background_id}/admin", response_model=CharacterBackgroundResponse
)
@inject
async def update_character_background(
    character_background_id: UUID,
    data: CharacterBackgroundUpdate,
    _: int = Depends(admin_user_provider),
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
    "/{character_background_id}/admin", status_code=status.HTTP_204_NO_CONTENT
)
@inject
async def delete_character_background(
    character_background_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: RemoveCharacterBackgroundUseCase = Depends(
        Provide[ApplicationContainer.remove_character_background_use_case]
    ),
):
    """Удалить фон персонажа (требуется админ-доступ)"""
    try:
        await use_case.execute(character_background_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.patch(
    "/{character_background_id}/activate", response_model=CharacterBackgroundResponse
)
@inject
async def activate_my_background(
    character_background_id: UUID,
    payload: TokenPayload = Depends(get_access_token_payload),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    get_background_use_case: GetCharacterBackgroundUseCase = Depends(
        Provide[ApplicationContainer.get_character_background_use_case]
    ),
    use_case: ActivateBackgroundUseCase = Depends(
        Provide[ApplicationContainer.activate_background_use_case]
    ),
):
    """Активировать фон"""
    telegram_id = int(payload.sub)
    try:
        character = await get_character_use_case.execute(telegram_id)
        background = await get_background_use_case.execute(character_background_id)

        if background.character_id != character.id:
            raise NotFoundException(
                detail="Background does not belong to your character"
            )

        updated_background = await use_case.execute(character_background_id)
        return CharacterBackgroundResponse.model_validate(updated_background)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.patch(
    "/{character_background_id}/deactivate", response_model=CharacterBackgroundResponse
)
@inject
async def deactivate_my_background(
    character_background_id: UUID,
    payload: TokenPayload = Depends(get_access_token_payload),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    get_background_use_case: GetCharacterBackgroundUseCase = Depends(
        Provide[ApplicationContainer.get_character_background_use_case]
    ),
    use_case: DeactivateBackgroundUseCase = Depends(
        Provide[ApplicationContainer.deactivate_background_use_case]
    ),
):
    """Деактивировать фон"""
    telegram_id = int(payload.sub)
    try:
        character = await get_character_use_case.execute(telegram_id)
        background = await get_background_use_case.execute(character_background_id)

        if background.character_id != character.id:
            raise NotFoundException(
                detail="Background does not belong to your character"
            )

        updated_background = await use_case.execute(character_background_id)
        return CharacterBackgroundResponse.model_validate(updated_background)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.patch(
    "/{character_background_id}/favourite", response_model=CharacterBackgroundResponse
)
@inject
async def toggle_favourite_background(
    character_background_id: UUID,
    payload: TokenPayload = Depends(get_access_token_payload),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    get_background_use_case: GetCharacterBackgroundUseCase = Depends(
        Provide[ApplicationContainer.get_character_background_use_case]
    ),
    use_case: ToggleFavouriteBackgroundUseCase = Depends(
        Provide[ApplicationContainer.toggle_favourite_background_use_case]
    ),
):
    """Добавить/убрать фон из избранного"""
    telegram_id = int(payload.sub)
    try:
        character = await get_character_use_case.execute(telegram_id)
        background = await get_background_use_case.execute(character_background_id)

        if background.character_id != character.id:
            raise NotFoundException(
                detail="Background does not belong to your character"
            )

        updated_background = await use_case.execute(character_background_id)
        return CharacterBackgroundResponse.model_validate(updated_background)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get("/me", response_model=list[CharacterBackgroundResponse])
@inject
async def list_my_backgrounds(
    payload: TokenPayload = Depends(get_access_token_payload),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: ListCharacterBackgroundsUseCase = Depends(
        Provide[ApplicationContainer.list_character_backgrounds_use_case]
    ),
):
    """Получить список купленных фонов текущего пользователя"""
    telegram_id = int(payload.sub)
    try:
        character = await get_character_use_case.execute(telegram_id)
        backgrounds = await use_case.execute(character.id)
        return [CharacterBackgroundResponse.model_validate(bg) for bg in backgrounds]
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/purchase",
    response_model=CharacterBackgroundResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def purchase_background(
    background_id: UUID = Query(..., description="ID фона для покупки"),
    payload: TokenPayload = Depends(get_access_token_payload),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: PurchaseBackgroundWithBalanceUseCase = Depends(
        Provide[ApplicationContainer.purchase_background_with_balance_use_case]
    ),
):
    """Купить фон (списываются монетки с баланса)"""
    telegram_id = int(payload.sub)
    try:
        character = await get_character_use_case.execute(telegram_id)

        input_data = PurchaseBackgroundWithBalanceInput(
            user_tg_id=telegram_id,
            character_id=character.id,
            background_id=background_id,
        )
        purchased_background = await use_case.execute(input_data)
        return CharacterBackgroundResponse.model_validate(purchased_background)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))
