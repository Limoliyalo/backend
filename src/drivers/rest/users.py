import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.domain.exceptions import UserNotFoundException
from src.drivers.rest.exceptions import BadRequestException, NotFoundException
from src.drivers.rest.schemas.users import (
    UserCreate,
    UserResponse,
    UserUpdate,
)
from src.use_cases.users.manage_users import (
    CreateUserInput,
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserInput,
    UpdateUserUseCase,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/admin", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
@inject
async def list_users(
    _: int = Depends(admin_user_provider),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    use_case: ListUsersUseCase = Depends(
        Provide[ApplicationContainer.list_users_use_case]
    ),
):
    """Получить список всех пользователей (требуется админ-доступ)"""
    users = await use_case.execute(limit=limit, offset=offset)
    return [UserResponse.model_validate(u) for u in users]


@router.get(
    "/admin/{telegram_id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
@inject
async def get_user(
    telegram_id: int,
    _: int = Depends(admin_user_provider),
    use_case: GetUserUseCase = Depends(Provide[ApplicationContainer.get_user_use_case]),
):
    """Получить пользователя по Telegram ID (требуется админ-доступ)"""
    logger.info(
        {"action": "get_user", "stage": "start", "data": {"telegram_id": telegram_id}}
    )

    try:
        user = await use_case.execute(telegram_id)
        response = UserResponse.model_validate(user)

        logger.info(
            {
                "action": "get_user",
                "stage": "end",
                "data": {"telegram_id": telegram_id, "success": True},
            }
        )
        return response
    except UserNotFoundException as e:
        logger.warning(
            {
                "action": "get_user",
                "stage": "not_found",
                "data": {"telegram_id": telegram_id},
            }
        )
        raise NotFoundException(detail=str(e))


@router.post("/admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
    data: UserCreate,
    use_case: CreateUserUseCase = Depends(
        Provide[ApplicationContainer.create_user_use_case]
    ),
    _: int = Depends(admin_user_provider),
):
    """Создать нового пользователя (требуется админ-доступ)"""
    logger.info(
        {
            "action": "create_user",
            "stage": "start",
            "data": {
                "telegram_id": data.telegram_id,
                "is_active": data.is_active,
                "balance": data.balance,
            },
        }
    )

    try:
        input_data = CreateUserInput(
            telegram_id=data.telegram_id,
            password=data.password,
            is_active=data.is_active,
            balance=data.balance,
        )
        user = await use_case.execute(input_data)
        response = UserResponse.model_validate(user)

        logger.info(
            {
                "action": "create_user",
                "stage": "end",
                "data": {"telegram_id": data.telegram_id, "success": True},
            }
        )
        return response
    except ValueError as e:
        logger.error(
            {
                "action": "create_user",
                "stage": "error",
                "data": {"telegram_id": data.telegram_id, "error": str(e)},
            }
        )
        raise BadRequestException(detail=str(e))


@router.put(
    "/admin/{telegram_id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
@inject
async def update_user(
    telegram_id: int,
    data: UserUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdateUserUseCase = Depends(
        Provide[ApplicationContainer.update_user_use_case]
    ),
):
    """Обновить пользователя (требуется админ-доступ)"""
    try:
        input_data = UpdateUserInput(
            telegram_id=telegram_id,
            password=data.password,
            is_active=data.is_active,
            balance=data.balance,
        )
        user = await use_case.execute(input_data)
        return UserResponse.model_validate(user)
    except UserNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))


@router.delete("/admin/{telegram_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_user(
    telegram_id: int,
    _: int = Depends(admin_user_provider),
    use_case: DeleteUserUseCase = Depends(
        Provide[ApplicationContainer.delete_user_use_case]
    ),
):
    """Удалить пользователя (требуется админ-доступ)"""
    try:
        await use_case.execute(telegram_id)
    except UserNotFoundException as e:
        raise NotFoundException(detail=str(e))
