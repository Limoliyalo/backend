from datetime import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.dependencies import get_telegram_current_user
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import BadRequestException, NotFoundException
from src.drivers.rest.schemas.food_entries import (
    FoodEntriesDayResponse,
    FoodEntryCreate,
    FoodEntryDelete,
    FoodEntryResponse,
    FoodEntryUpdate,
)
from src.use_cases.characters.get_character import GetCharacterByUserUseCase
from src.use_cases.daily_activities.recalculate_xp import (
    RecalculateDailyXpInput,
    RecalculateDailyXpUseCase,
)
from src.use_cases.food_entries.manage_food_entries import (
    CreateFoodEntryInput,
    CreateFoodEntryUseCase,
    DeleteFoodEntryUseCase,
    ListFoodEntriesForDayUseCase,
    UpdateFoodEntryInput,
    UpdateFoodEntryUseCase,
)

router = APIRouter(prefix="/food-entries", tags=["Food Entries"])


@router.get("/me", response_model=FoodEntriesDayResponse)
@inject
async def list_my_food_entries(
    day: datetime = Query(
        ..., description="День для получения записей еды"
    ),
    telegram_id: int = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: ListFoodEntriesForDayUseCase = Depends(
        Provide[ApplicationContainer.list_food_entries_for_day_use_case]
    ),
):
    character = await get_character_use_case.execute(telegram_id)
    result = await use_case.execute(character.id, day)
    return FoodEntriesDayResponse.model_validate(result)


@router.post(
    "/me", response_model=FoodEntryResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_my_food_entry(
    data: FoodEntryCreate,
    telegram_id: int = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: CreateFoodEntryUseCase = Depends(
        Provide[ApplicationContainer.create_food_entry_use_case]
    ),
    recalculate_xp_use_case: RecalculateDailyXpUseCase = Depends(
        Provide[ApplicationContainer.recalculate_daily_xp_use_case]
    ),
):
    try:
        character = await get_character_use_case.execute(telegram_id)
        entry = await use_case.execute(
            CreateFoodEntryInput(
                character_id=character.id,
                consumed_at=data.consumed_at,
                meal_type=data.meal_type,
                title=data.title,
                calories=data.calories,
                protein_g=data.protein_g,
                fat_g=data.fat_g,
                carbs_g=data.carbs_g,
                notes=data.notes,
            )
        )
        await recalculate_xp_use_case.execute(
            RecalculateDailyXpInput(character_id=character.id, date=entry.consumed_at)
        )
        return FoodEntryResponse.model_validate(entry)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))


@router.patch("/me", response_model=FoodEntryResponse)
@inject
async def update_my_food_entry(
    data: FoodEntryUpdate,
    telegram_id: int = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: UpdateFoodEntryUseCase = Depends(
        Provide[ApplicationContainer.update_food_entry_use_case]
    ),
    recalculate_xp_use_case: RecalculateDailyXpUseCase = Depends(
        Provide[ApplicationContainer.recalculate_daily_xp_use_case]
    ),
):
    try:
        character = await get_character_use_case.execute(telegram_id)
        entry = await use_case.execute(
            UpdateFoodEntryInput(
                entry_id=data.entry_id,
                character_id=character.id,
                consumed_at=data.consumed_at,
                meal_type=data.meal_type,
                title=data.title,
                calories=data.calories,
                protein_g=data.protein_g,
                fat_g=data.fat_g,
                carbs_g=data.carbs_g,
                notes=data.notes,
                fields_to_update=set(data.model_fields_set) - {"entry_id"},
            )
        )
        await recalculate_xp_use_case.execute(
            RecalculateDailyXpInput(character_id=character.id, date=entry.consumed_at)
        )
        return FoodEntryResponse.model_validate(entry)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_my_food_entry(
    data: FoodEntryDelete,
    telegram_id: int = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: DeleteFoodEntryUseCase = Depends(
        Provide[ApplicationContainer.delete_food_entry_use_case]
    ),
    recalculate_xp_use_case: RecalculateDailyXpUseCase = Depends(
        Provide[ApplicationContainer.recalculate_daily_xp_use_case]
    ),
):
    try:
        character = await get_character_use_case.execute(telegram_id)
        sync_day = await use_case.execute(data.entry_id, character.id)
        await recalculate_xp_use_case.execute(
            RecalculateDailyXpInput(character_id=character.id, date=sync_day)
        )
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))
