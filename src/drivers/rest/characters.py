import logging
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.core.auth.dependencies import get_telegram_current_user
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects.telegram_id import TelegramId
from src.adapters.repositories.exceptions import (
    RepositoryError,
    IntegrityConstraintError,
    DuplicateEntityError,
)
from src.drivers.rest.exceptions import NotFoundException, BadRequestException
from src.drivers.rest.schemas.characters import (
    CharacterCreate,
    CharacterResponse,
    CharacterUpdate,
    CharacterUserCreate,
    CharacterUserUpdate,
)
from src.use_cases.characters.create_character import (
    CreateCharacterInput,
    CreateCharacterUseCase,
)
from src.use_cases.characters.delete_character import DeleteCharacterUseCase
from src.use_cases.characters.get_character import (
    GetCharacterByIdUseCase,
    GetCharacterByUserUseCase,
    ListCharactersUseCase,
)
from src.use_cases.characters.update_character import (
    UpdateCharacterInput,
    UpdateCharacterUseCase,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/characters", tags=["Characters"])


@router.get("/admin", response_model=list[CharacterResponse])
@inject
async def list_characters(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _: int = Depends(admin_user_provider),
    use_case: ListCharactersUseCase = Depends(
        Provide[ApplicationContainer.list_characters_use_case]
    ),
):
    """Получить список всех персонажей (требуется админ-доступ)"""
    characters = await use_case.execute(limit=limit, offset=offset)
    return [CharacterResponse.model_validate(char) for char in characters]


@router.get("/{character_id}/admin", response_model=CharacterResponse)
@inject
async def get_character(
    character_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: GetCharacterByIdUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_id_use_case]
    ),
):
    """Получить персонажа по ID (требуется админ-доступ)"""
    try:
        character = await use_case.execute(character_id)
        return CharacterResponse.model_validate(character)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/admin", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_character(
    data: CharacterCreate,
    _: int = Depends(admin_user_provider),
    use_case: CreateCharacterUseCase = Depends(
        Provide[ApplicationContainer.create_character_use_case]
    ),
):
    """Создать нового персонажа (требуется админ-доступ)"""
    try:
        input_data = CreateCharacterInput(
            user_tg_id=data.user_tg_id,
            name=data.name,
            sex=data.sex,
            current_mood=data.current_mood,
            level=data.level,
            total_experience=data.total_experience,
        )
        character = await use_case.execute(input_data)
        return CharacterResponse.model_validate(character)
    except DuplicateEntityError as e:
        logger.error(f"DuplicateEntityError in create_character: {e}")
        raise BadRequestException(detail="Character already exists for this user")
    except IntegrityConstraintError as e:
        logger.error(f"IntegrityConstraintError in create_character: {e}")
        raise BadRequestException(detail="Integrity constraint violated")
    except RepositoryError as e:
        logger.error(f"RepositoryError in create_character: {e}")
        raise BadRequestException(detail=str(e))


@router.patch("/{character_id}/admin", response_model=CharacterResponse)
@inject
async def update_character(
    character_id: UUID,
    data: CharacterUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdateCharacterUseCase = Depends(
        Provide[ApplicationContainer.update_character_use_case]
    ),
):
    """Обновить персонажа (требуется админ-доступ)"""
    try:
        input_data = UpdateCharacterInput(
            character_id=character_id,
            name=data.name,
            sex=data.sex,
            current_mood=data.current_mood,
        )
        character = await use_case.execute(input_data)
        return CharacterResponse.model_validate(character)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{character_id}/admin", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_character(
    character_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: DeleteCharacterUseCase = Depends(
        Provide[ApplicationContainer.delete_character_use_case]
    ),
):
    """Удалить персонажа (требуется админ-доступ)"""
    try:
        await use_case.execute(character_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get("/me", response_model=CharacterResponse)
@inject
async def get_my_character(
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
):
    """Получить персонажа текущего пользователя"""
    try:
        character = await use_case.execute(telegram_id.value)
        return CharacterResponse.model_validate(character)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/me", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_my_character(
    data: CharacterUserCreate,
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    use_case: CreateCharacterUseCase = Depends(
        Provide[ApplicationContainer.create_character_use_case]
    ),
):
    """Создать персонажа для текущего пользователя (только name и sex)"""
    try:
        input_data = CreateCharacterInput(
            user_tg_id=telegram_id.value,
            name=data.name,
            sex=data.sex,
            current_mood="neutral",
            level=1,
            total_experience=0,
        )
        character = await use_case.execute(input_data)
        return CharacterResponse.model_validate(character)
    except DuplicateEntityError:
        raise BadRequestException(detail="Character already exists for this user")
    except IntegrityConstraintError:
        raise BadRequestException(detail="Integrity constraint violated")
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))


@router.patch("/me", response_model=CharacterResponse)
@inject
async def update_my_character(
    data: CharacterUserUpdate,
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    update_use_case: UpdateCharacterUseCase = Depends(
        Provide[ApplicationContainer.update_character_use_case]
    ),
):
    """Обновить персонажа текущего пользователя (только name и sex)"""
    try:

        character = await get_character_use_case.execute(telegram_id.value)

        input_data = UpdateCharacterInput(
            character_id=character.id,
            name=data.name,
            sex=data.sex,
            current_mood=None,
        )
        updated_character = await update_use_case.execute(input_data)
        return CharacterResponse.model_validate(updated_character)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_my_character(
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    delete_use_case: DeleteCharacterUseCase = Depends(
        Provide[ApplicationContainer.delete_character_use_case]
    ),
):
    """Удалить персонажа текущего пользователя"""
    try:

        character = await get_character_use_case.execute(telegram_id.value)

        await delete_use_case.execute(character.id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
