from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.activities import MoodHistoryCreate, MoodHistoryResponse
from src.use_cases.mood_history.manage_mood_history import (
    CreateMoodHistoryInput,
    CreateMoodHistoryUseCase,
    DeleteMoodHistoryUseCase,
    GetMoodHistoryUseCase,
    ListMoodHistoryForCharacterUseCase,
)

router = APIRouter(prefix="/mood-history", tags=["Mood History"])


@router.post(
    "", response_model=MoodHistoryResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_mood_history(
    data: MoodHistoryCreate,
    use_case: CreateMoodHistoryUseCase = Depends(
        Provide[ApplicationContainer.create_mood_history_use_case]
    ),
):
    """Создать запись о настроении"""
    input_data = CreateMoodHistoryInput(
        character_id=data.character_id,
        mood=data.mood,
        trigger=data.trigger,
    )
    mood_history = await use_case.execute(input_data)
    return MoodHistoryResponse.model_validate(mood_history)


@router.get(
    "/character/{character_id}",
    response_model=list[MoodHistoryResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_mood_history_for_character(
    character_id: UUID,
    limit: int = Query(100, ge=1, le=500),
    use_case: ListMoodHistoryForCharacterUseCase = Depends(
        Provide[ApplicationContainer.list_mood_history_for_character_use_case]
    ),
):
    """Получить историю настроения для персонажа"""
    mood_history = await use_case.execute(character_id, limit=limit)
    return [MoodHistoryResponse.model_validate(mh) for mh in mood_history]


@router.get(
    "/{mood_history_id}",
    response_model=MoodHistoryResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_mood_history(
    mood_history_id: UUID,
    use_case: GetMoodHistoryUseCase = Depends(
        Provide[ApplicationContainer.get_mood_history_use_case]
    ),
):
    """Получить запись о настроении по ID"""
    try:
        mood_history = await use_case.execute(mood_history_id)
        return MoodHistoryResponse.model_validate(mood_history)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{mood_history_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_mood_history(
    mood_history_id: UUID,
    use_case: DeleteMoodHistoryUseCase = Depends(
        Provide[ApplicationContainer.delete_mood_history_use_case]
    ),
):
    """Удалить запись о настроении"""
    try:
        await use_case.execute(mood_history_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
