from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth import get_admin_user
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.characters import (
    CharacterCreate,
    CharacterResponse,
    CharacterUpdate,
)
from src.use_cases.characters.create_character import (
    CreateCharacterInput,
    CreateCharacterUseCase,
)
from src.use_cases.characters.delete_character import DeleteCharacterUseCase
from src.use_cases.characters.get_character import (
    GetCharacterByIdUseCase,
    ListCharactersUseCase,
)
from src.use_cases.characters.update_character import (
    UpdateCharacterInput,
    UpdateCharacterUseCase,
)

router = APIRouter(prefix="/characters", tags=["Characters"])


@router.get("/admin", response_model=list[CharacterResponse])
@inject
async def list_characters(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _: int = Depends(get_admin_user),
    use_case: ListCharactersUseCase = Depends(
        Provide[ApplicationContainer.list_characters_use_case]
    ),
):
    """Получить список всех персонажей (требуется админ-доступ)"""
    characters = await use_case.execute(limit=limit, offset=offset)
    return [CharacterResponse.model_validate(char) for char in characters]


@router.get("/admin/{character_id}", response_model=CharacterResponse)
@inject
async def get_character(
    character_id: UUID,
    _: int = Depends(get_admin_user),
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
    _: int = Depends(get_admin_user),
    use_case: CreateCharacterUseCase = Depends(
        Provide[ApplicationContainer.create_character_use_case]
    ),
):
    """Создать нового персонажа (требуется админ-доступ)"""
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


@router.patch("/admin/{character_id}", response_model=CharacterResponse)
@inject
async def update_character(
    character_id: UUID,
    data: CharacterUpdate,
    _: int = Depends(get_admin_user),
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


@router.delete("/admin/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_character(
    character_id: UUID,
    _: int = Depends(get_admin_user),
    use_case: DeleteCharacterUseCase = Depends(
        Provide[ApplicationContainer.delete_character_use_case]
    ),
):
    """Удалить персонажа (требуется админ-доступ)"""
    try:
        await use_case.execute(character_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
