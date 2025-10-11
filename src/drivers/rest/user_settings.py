from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.container import ApplicationContainer
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.user_settings import (
    UserSettingsResponse,
    UserSettingsUpdate,
)
from src.use_cases.user_settings.manage_settings import (
    GetUserSettingsUseCase,
    UpdateUserSettingsInput,
    UpsertUserSettingsUseCase,
)

router = APIRouter(prefix="/user-settings", tags=["user-settings"])


@router.get("/{user_tg_id}", response_model=UserSettingsResponse)
@inject
async def get_user_settings(
    user_tg_id: int,
    use_case: GetUserSettingsUseCase = Depends(
        Provide[ApplicationContainer.get_user_settings_use_case]
    ),
):
    """Получить настройки пользователя"""
    try:
        settings = await use_case.execute(user_tg_id)
        return UserSettingsResponse.model_validate(settings)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.put("/{user_tg_id}", response_model=UserSettingsResponse)
@inject
async def upsert_user_settings(
    user_tg_id: int,
    data: UserSettingsUpdate,
    use_case: UpsertUserSettingsUseCase = Depends(
        Provide[ApplicationContainer.upsert_user_settings_use_case]
    ),
):
    """Создать или обновить настройки пользователя"""
    input_data = UpdateUserSettingsInput(
        user_tg_id=user_tg_id,
        quiet_start_time=data.quiet_start_time,
        quiet_end_time=data.quiet_end_time,
        muted_days=data.muted_days,
        do_not_disturb=data.do_not_disturb,
    )
    settings = await use_case.execute(input_data)
    return UserSettingsResponse.model_validate(settings)
