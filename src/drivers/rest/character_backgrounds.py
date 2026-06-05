from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.core.auth.dependencies import get_telegram_current_user
from src.domain.exceptions import EntityNotFoundException
from src.adapters.repositories.exceptions import RepositoryError
from src.drivers.rest.exceptions import NotFoundException, BadRequestException
from src.drivers.rest.schemas.character_backgrounds import (
    CharacterBackgroundDelete,
    CharacterBackgroundPurchase,
    CharacterBackgroundResponse,
    CharacterBackgroundToggleFavorite,
    CharacterBackgroundUpdate,
    CharacterBackgroundUserPurchase,
    EquipBackgroundRequest,
    UnequipBackgroundRequest,
)
from src.use_cases.character_backgrounds.manage_character_backgrounds import (
    EquipBackgroundUseCase,
    GetCharacterBackgroundUseCase,
    ListCharacterBackgroundsUseCase,
    PurchaseBackgroundInput,
    PurchaseBackgroundUseCase,
    PurchaseBackgroundWithBalanceInput,
    PurchaseBackgroundWithBalanceUseCase,
    RemoveCharacterBackgroundUseCase,
    ToggleFavoriteBackgroundInput,
    ToggleFavoriteBackgroundUseCase,
    UnequipBackgroundUseCase,
    UpdateCharacterBackgroundInput,
    UpdateCharacterBackgroundUseCase,
)
from src.use_cases.characters.get_character import GetCharacterByUserUseCase

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
    try:
        backgrounds = await use_case.execute(character_id)
        return [
            CharacterBackgroundResponse.model_validate(background)
            for background in backgrounds
        ]
    except RepositoryError as e:
        raise BadRequestException(f"Database error: {str(e)}")


@router.get("/admin/{background_id}", response_model=CharacterBackgroundResponse)
@inject
async def get_character_background(
    background_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: GetCharacterBackgroundUseCase = Depends(
        Provide[ApplicationContainer.get_character_background_use_case]
    ),
):
    """Получить фон персонажа по ID (требуется админ-доступ)"""
    try:
        background = await use_case.execute(background_id)
        return CharacterBackgroundResponse.model_validate(background)
    except EntityNotFoundException:
        raise NotFoundException("Character background not found")
    except ValueError as e:
        raise BadRequestException(str(e))
    except RepositoryError as e:
        raise BadRequestException(f"Database error: {str(e)}")


@router.post(
    "/admin",
    response_model=CharacterBackgroundResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_character_background(
    background_data: CharacterBackgroundPurchase,
    _: int = Depends(admin_user_provider),
    use_case: PurchaseBackgroundUseCase = Depends(
        Provide[ApplicationContainer.purchase_background_use_case]
    ),
):
    """Создать фон персонажа (требуется админ-доступ)"""
    try:
        input_data = PurchaseBackgroundInput(
            character_id=background_data.character_id,
            background_id=background_data.background_id,
            is_active=background_data.is_active,
            is_favorite=background_data.is_favorite,
        )
        background = await use_case.execute(input_data)
        return CharacterBackgroundResponse.model_validate(background)
    except RepositoryError as e:
        raise BadRequestException(f"Database error: {str(e)}")


@router.put("/admin", response_model=CharacterBackgroundResponse)
@inject
async def update_character_background(
    background_data: CharacterBackgroundUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdateCharacterBackgroundUseCase = Depends(
        Provide[ApplicationContainer.update_character_background_use_case]
    ),
):
    """Обновить фон персонажа (требуется админ-доступ)"""
    try:
        input_data = UpdateCharacterBackgroundInput(
            character_background_id=background_data.background_id,
            is_active=background_data.is_active,
            is_favorite=background_data.is_favorite,
        )
        background = await use_case.execute(input_data)
        return CharacterBackgroundResponse.model_validate(background)
    except EntityNotFoundException:
        raise NotFoundException("Character background not found")
    except ValueError as e:
        raise BadRequestException(str(e))
    except RepositoryError as e:
        raise BadRequestException(f"Database error: {str(e)}")


@router.delete("/admin", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_character_background(
    data: CharacterBackgroundDelete,
    _: int = Depends(admin_user_provider),
    use_case: RemoveCharacterBackgroundUseCase = Depends(
        Provide[ApplicationContainer.remove_character_background_use_case]
    ),
):
    """Удалить фон персонажа (требуется админ-доступ)"""
    try:
        await use_case.execute(data.background_id)
    except EntityNotFoundException:
        raise NotFoundException("Character background not found")
    except ValueError as e:
        raise BadRequestException(str(e))
    except RepositoryError as e:
        raise BadRequestException(f"Database error: {str(e)}")


@router.post("/admin/equip", response_model=CharacterBackgroundResponse)
@inject
async def equip_background(
    request: EquipBackgroundRequest,
    _: int = Depends(admin_user_provider),
    use_case: EquipBackgroundUseCase = Depends(
        Provide[ApplicationContainer.equip_background_use_case]
    ),
):
    """Экипировать фон (требуется админ-доступ)"""
    try:
        background = await use_case.execute(request.background_id)
        return CharacterBackgroundResponse.model_validate(background)
    except EntityNotFoundException:
        raise NotFoundException("Character background not found")
    except ValueError as e:
        raise BadRequestException(str(e))
    except RepositoryError as e:
        raise BadRequestException(f"Database error: {str(e)}")


@router.post("/admin/unequip", response_model=CharacterBackgroundResponse)
@inject
async def unequip_background(
    request: UnequipBackgroundRequest,
    _: int = Depends(admin_user_provider),
    use_case: UnequipBackgroundUseCase = Depends(
        Provide[ApplicationContainer.unequip_background_use_case]
    ),
):
    """Снять фон (требуется админ-доступ)"""
    try:
        background = await use_case.execute(request.background_id)
        return CharacterBackgroundResponse.model_validate(background)
    except EntityNotFoundException:
        raise NotFoundException("Character background not found")
    except RepositoryError as e:
        raise BadRequestException(f"Database error: {str(e)}")


@router.post(
    "/admin/toggle-favorite",
    response_model=CharacterBackgroundResponse,
)
@inject
async def toggle_favorite_background(
    background_data: CharacterBackgroundToggleFavorite,
    _: int = Depends(admin_user_provider),
    use_case: ToggleFavoriteBackgroundUseCase = Depends(
        Provide[ApplicationContainer.toggle_favorite_background_use_case]
    ),
):
    """Переключить избранное для фона (требуется админ-доступ)"""
    try:
        input_data = ToggleFavoriteBackgroundInput(
            character_id=background_data.character_id,
            background_id=background_data.background_id,
        )
        background = await use_case.execute(input_data)
        return CharacterBackgroundResponse.model_validate(background)
    except EntityNotFoundException:
        raise NotFoundException("Character background not found")
    except RepositoryError as e:
        raise BadRequestException(f"Database error: {str(e)}")


@router.get("/me", response_model=list[CharacterBackgroundResponse])
@inject
async def list_user_character_backgrounds(
    telegram_id: int = Depends(get_telegram_current_user),
    use_case: ListCharacterBackgroundsUseCase = Depends(
        Provide[ApplicationContainer.list_character_backgrounds_use_case]
    ),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
):
    """Получить список фонов персонажа пользователя"""
    try:
        character = await get_character_use_case.execute(telegram_id)
        backgrounds = await use_case.execute(character.id)
        return [
            CharacterBackgroundResponse.model_validate(background)
            for background in backgrounds
        ]
    except EntityNotFoundException:
        raise NotFoundException("Character not found")
    except RepositoryError as e:
        raise BadRequestException(f"Database error: {str(e)}")


@router.get("/me/{background_id}", response_model=CharacterBackgroundResponse)
@inject
async def get_user_character_background(
    background_id: UUID,
    telegram_id: int = Depends(get_telegram_current_user),
    use_case: GetCharacterBackgroundUseCase = Depends(
        Provide[ApplicationContainer.get_character_background_use_case]
    ),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
):
    """Получить фон персонажа пользователя по ID"""
    try:
        # Сначала получаем персонажа пользователя
        character = await get_character_use_case.execute(telegram_id)

        # Затем получаем фон и проверяем, что он принадлежит этому персонажу
        background = await use_case.execute(background_id)

        # Проверяем, что фон принадлежит персонажу пользователя
        if background.character_id != character.id:
            raise NotFoundException("Character background not found")

        return CharacterBackgroundResponse.model_validate(background)
    except EntityNotFoundException:
        raise NotFoundException("Character background not found")
    except RepositoryError as e:
        raise BadRequestException(f"Database error: {str(e)}")


@router.post(
    "/me/purchase",
    response_model=CharacterBackgroundResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def purchase_background(
    background_data: CharacterBackgroundUserPurchase,
    telegram_id: int = Depends(get_telegram_current_user),
    use_case: PurchaseBackgroundWithBalanceUseCase = Depends(
        Provide[ApplicationContainer.purchase_background_with_balance_use_case]
    ),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
):
    """Купить фон для персонажа"""
    try:
        character = await get_character_use_case.execute(telegram_id)
        input_data = PurchaseBackgroundWithBalanceInput(
            user_tg_id=telegram_id,
            character_id=character.id,
            background_id=background_data.background_id,
        )
        background = await use_case.execute(input_data)
        return CharacterBackgroundResponse.model_validate(background)
    except EntityNotFoundException as e:
        raise NotFoundException(str(e))
    except ValueError as e:
        raise BadRequestException(str(e))
    except RepositoryError as e:
        raise BadRequestException(f"Database error: {str(e)}")


@router.put("/me", response_model=CharacterBackgroundResponse)
@inject
async def update_user_character_background(
    background_data: CharacterBackgroundUpdate,
    telegram_id: int = Depends(get_telegram_current_user),
    use_case: UpdateCharacterBackgroundUseCase = Depends(
        Provide[ApplicationContainer.update_character_background_use_case]
    ),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    get_background_use_case: GetCharacterBackgroundUseCase = Depends(
        Provide[ApplicationContainer.get_character_background_use_case]
    ),
):
    """Обновить фон персонажа пользователя"""
    try:
        # Сначала получаем персонажа пользователя
        character = await get_character_use_case.execute(telegram_id)

        # Проверяем, что фон принадлежит персонажу пользователя
        background = await get_background_use_case.execute(
            background_data.background_id
        )
        if background.character_id != character.id:
            raise NotFoundException("Character background not found")
        if background_data.is_active and not background.is_purchased:
            raise NotFoundException("Character background not found")

        input_data = UpdateCharacterBackgroundInput(
            character_background_id=background_data.background_id,
            is_active=background_data.is_active,
            is_favorite=background_data.is_favorite,
        )
        background = await use_case.execute(input_data)
        return CharacterBackgroundResponse.model_validate(background)
    except EntityNotFoundException:
        raise NotFoundException("Character background not found")
    except ValueError as e:
        raise BadRequestException(str(e))
    except RepositoryError as e:
        raise BadRequestException(f"Database error: {str(e)}")


@router.post("/me/equip", response_model=CharacterBackgroundResponse)
@inject
async def equip_user_background(
    request: EquipBackgroundRequest,
    telegram_id: int = Depends(get_telegram_current_user),
    use_case: EquipBackgroundUseCase = Depends(
        Provide[ApplicationContainer.equip_background_use_case]
    ),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    list_backgrounds_use_case: ListCharacterBackgroundsUseCase = Depends(
        Provide[ApplicationContainer.list_character_backgrounds_use_case]
    ),
):
    """Экипировать фон"""
    try:
        # Сначала получаем персонажа пользователя
        character = await get_character_use_case.execute(telegram_id)

        # Запрос принимает catalog background_id, а equip use case работает
        # с id записи character_backgrounds.
        backgrounds = await list_backgrounds_use_case.execute(character.id)
        character_background = next(
            (
                background
                for background in backgrounds
                if background.background_id == request.background_id
            ),
            None,
        )
        if character_background is None or not character_background.is_purchased:
            raise NotFoundException("Character background not found")

        background = await use_case.execute(character_background.id)
        return CharacterBackgroundResponse.model_validate(background)
    except EntityNotFoundException:
        raise NotFoundException("Character background not found")
    except ValueError as e:
        raise BadRequestException(str(e))
    except RepositoryError as e:
        raise BadRequestException(f"Database error: {str(e)}")


@router.post("/me/unequip", response_model=CharacterBackgroundResponse)
@inject
async def unequip_user_background(
    request: UnequipBackgroundRequest,
    telegram_id: int = Depends(get_telegram_current_user),
    use_case: UnequipBackgroundUseCase = Depends(
        Provide[ApplicationContainer.unequip_background_use_case]
    ),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    list_backgrounds_use_case: ListCharacterBackgroundsUseCase = Depends(
        Provide[ApplicationContainer.list_character_backgrounds_use_case]
    ),
):
    """Снять фон"""
    try:
        # Сначала получаем персонажа пользователя
        character = await get_character_use_case.execute(telegram_id)

        # Запрос принимает catalog background_id, а unequip use case работает
        # с id записи character_backgrounds.
        backgrounds = await list_backgrounds_use_case.execute(character.id)
        character_background = next(
            (
                background
                for background in backgrounds
                if background.background_id == request.background_id
            ),
            None,
        )
        if character_background is None or not character_background.is_purchased:
            raise NotFoundException("Character background not found")

        background = await use_case.execute(character_background.id)
        return CharacterBackgroundResponse.model_validate(background)
    except EntityNotFoundException:
        raise NotFoundException("Character background not found")
    except RepositoryError as e:
        raise BadRequestException(f"Database error: {str(e)}")
