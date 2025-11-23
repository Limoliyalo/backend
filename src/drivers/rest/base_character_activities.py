from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.core.auth.dependencies import get_telegram_current_user
from src.domain.exceptions import EntityNotFoundException
from src.adapters.repositories.exceptions import RepositoryError
from src.drivers.rest.exceptions import BadRequestException, NotFoundException
from src.drivers.rest.schemas.activities import (
    BaseCharacterActivityCreate,
    BaseCharacterActivityDelete,
    BaseCharacterActivityResponse,
    BaseCharacterActivityUpdate,
)
from src.use_cases.characters.get_character import GetCharacterByUserUseCase
from src.use_cases.base_character_activities.manage_base_character_activities import (
    CreateBaseCharacterActivityInput,
    CreateBaseCharacterActivityUseCase,
    DeleteBaseCharacterActivityUseCase,
    GetBaseCharacterActivityUseCase,
    ListBaseCharacterActivitiesUseCase,
    UpdateBaseCharacterActivityInput,
    UpdateBaseCharacterActivityUseCase,
)

router = APIRouter(
    prefix="/base-character-activities", tags=["Base Character Activities"]
)


@router.get(
    "/character/{character_id}/admin",
    response_model=list[BaseCharacterActivityResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_base_character_activities(
    character_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: ListBaseCharacterActivitiesUseCase = Depends(
        Provide[ApplicationContainer.list_base_character_activities_use_case]
    ),
):
    """Получить список базовых активностей персонажа (требуется админ-доступ)"""
    try:
        activities = await use_case.execute(character_id)
        return [BaseCharacterActivityResponse.model_validate(a) for a in activities]
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))


@router.get(
    "/{activity_id}/admin",
    response_model=BaseCharacterActivityResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_base_character_activity(
    activity_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: GetBaseCharacterActivityUseCase = Depends(
        Provide[ApplicationContainer.get_base_character_activity_use_case]
    ),
):
    """Получить базовую активность по ID (требуется админ-доступ)"""
    try:
        activity = await use_case.execute(activity_id)
        return BaseCharacterActivityResponse.model_validate(activity)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/admin",
    response_model=BaseCharacterActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_base_character_activity(
    character_id: UUID = Query(..., description="ID персонажа"),
    data: BaseCharacterActivityCreate = Body(...),
    _: int = Depends(admin_user_provider),
    use_case: CreateBaseCharacterActivityUseCase = Depends(
        Provide[ApplicationContainer.create_base_character_activity_use_case]
    ),
):
    """Создать базовую активность (требуется админ-доступ)"""
    try:
        input_data = CreateBaseCharacterActivityInput(
            character_id=character_id,
            activity_type_id=data.activity_type_id,
            goal=data.goal,
        )
        activity = await use_case.execute(input_data)
        return BaseCharacterActivityResponse.model_validate(activity)
    except ValueError as e:
        raise BadRequestException(detail=str(e))
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.patch(
    "/admin",
    response_model=BaseCharacterActivityResponse,
)
@inject
async def update_base_character_activity(
    data: BaseCharacterActivityUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdateBaseCharacterActivityUseCase = Depends(
        Provide[ApplicationContainer.update_base_character_activity_use_case]
    ),
):
    """Обновить базовую активность (требуется админ-доступ)"""
    try:
        input_data = UpdateBaseCharacterActivityInput(
            activity_id=data.activity_id,
            goal=data.goal,
        )
        activity = await use_case.execute(input_data)
        return BaseCharacterActivityResponse.model_validate(activity)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete(
    "/admin",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def delete_base_character_activity(
    data: BaseCharacterActivityDelete,
    _: int = Depends(admin_user_provider),
    use_case: DeleteBaseCharacterActivityUseCase = Depends(
        Provide[ApplicationContainer.delete_base_character_activity_use_case]
    ),
):
    """Удалить базовую активность (требуется админ-доступ)"""
    try:
        await use_case.execute(data.activity_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get(
    "/me",
    response_model=list[BaseCharacterActivityResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_my_base_character_activities(
    telegram_id: int = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: ListBaseCharacterActivitiesUseCase = Depends(
        Provide[ApplicationContainer.list_base_character_activities_use_case]
    ),
):
    """Получить список базовых активностей текущего пользователя"""
    try:
        character = await get_character_use_case.execute(telegram_id)
        activities = await use_case.execute(character.id)
        return [BaseCharacterActivityResponse.model_validate(a) for a in activities]
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/me",
    response_model=BaseCharacterActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_my_base_character_activity(
    data: BaseCharacterActivityCreate,
    telegram_id: int = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    use_case: CreateBaseCharacterActivityUseCase = Depends(
        Provide[ApplicationContainer.create_base_character_activity_use_case]
    ),
):
    """Добавить базовую активность для текущего пользователя"""
    try:
        character = await get_character_use_case.execute(telegram_id)
        input_data = CreateBaseCharacterActivityInput(
            character_id=character.id,
            activity_type_id=data.activity_type_id,
            goal=data.goal,
        )
        activity = await use_case.execute(input_data)
        return BaseCharacterActivityResponse.model_validate(activity)
    except ValueError as e:
        raise BadRequestException(detail=str(e))
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.patch(
    "/me",
    response_model=BaseCharacterActivityResponse,
)
@inject
async def update_my_base_character_activity(
    data: BaseCharacterActivityUpdate,
    telegram_id: int = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    get_activity_use_case: GetBaseCharacterActivityUseCase = Depends(
        Provide[ApplicationContainer.get_base_character_activity_use_case]
    ),
    update_use_case: UpdateBaseCharacterActivityUseCase = Depends(
        Provide[ApplicationContainer.update_base_character_activity_use_case]
    ),
):
    """Обновить базовую активность текущего пользователя"""
    try:
        character = await get_character_use_case.execute(telegram_id)
        activity = await get_activity_use_case.execute(data.activity_id)
        if activity.character_id != character.id:
            raise BadRequestException(
                detail="You can only update your own base activities"
            )

        input_data = UpdateBaseCharacterActivityInput(
            activity_id=data.activity_id,
            goal=data.goal,
        )
        updated_activity = await update_use_case.execute(input_data)
        return BaseCharacterActivityResponse.model_validate(updated_activity)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def delete_my_base_character_activity(
    data: BaseCharacterActivityDelete,
    telegram_id: int = Depends(get_telegram_current_user),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    get_activity_use_case: GetBaseCharacterActivityUseCase = Depends(
        Provide[ApplicationContainer.get_base_character_activity_use_case]
    ),
    delete_use_case: DeleteBaseCharacterActivityUseCase = Depends(
        Provide[ApplicationContainer.delete_base_character_activity_use_case]
    ),
):
    """Удалить базовую активность текущего пользователя"""
    try:
        character = await get_character_use_case.execute(telegram_id)
        activity = await get_activity_use_case.execute(data.activity_id)
        if activity.character_id != character.id:
            raise BadRequestException(
                detail="You can only delete your own base activities"
            )
        await delete_use_case.execute(data.activity_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
