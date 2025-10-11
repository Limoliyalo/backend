import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.domain.exceptions import UserNotFoundException
from src.drivers.rest.exceptions import BadRequestException, NotFoundException
from src.drivers.rest.schemas.users import (
    BalanceResponse,
    DepositRequest,
    UserCreate,
    UserResponse,
    UserUpdate,
    WithdrawRequest,
)
from src.use_cases.users.manage_users import (
    CreateUserInput,
    CreateUserUseCase,
    DeleteUserUseCase,
    DepositBalanceUseCase,
    DepositInput,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserInput,
    UpdateUserUseCase,
    WithdrawBalanceUseCase,
    WithdrawInput,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
@inject
async def list_users(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    use_case: ListUsersUseCase = Depends(
        Provide[ApplicationContainer.list_users_use_case]
    ),
):
    """Получить список пользователей"""
    users = await use_case.execute(limit=limit, offset=offset)
    return [UserResponse.model_validate(u) for u in users]


@router.get(
    "/{telegram_id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
@inject
async def get_user(
    telegram_id: int,
    use_case: GetUserUseCase = Depends(Provide[ApplicationContainer.get_user_use_case]),
):
    """Получить пользователя по Telegram ID"""
    logger.info({
        "action": "get_user",
        "stage": "start",
        "data": {"telegram_id": telegram_id}
    })
    
    try:
        user = await use_case.execute(telegram_id)
        response = UserResponse.model_validate(user)
        
        logger.info({
            "action": "get_user",
            "stage": "end",
            "data": {"telegram_id": telegram_id, "success": True}
        })
        return response
    except UserNotFoundException as e:
        logger.warning({
            "action": "get_user",
            "stage": "not_found",
            "data": {"telegram_id": telegram_id}
        })
        raise NotFoundException(detail=str(e))


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
    data: UserCreate,
    use_case: CreateUserUseCase = Depends(
        Provide[ApplicationContainer.create_user_use_case]
    ),
):
    """Создать нового пользователя"""
    logger.info({
        "action": "create_user",
        "stage": "start",
        "data": {
            "telegram_id": data.telegram_id,
            "is_active": data.is_active,
            "balance": data.balance
        }
    })
    
    try:
        input_data = CreateUserInput(
            telegram_id=data.telegram_id,
            password=data.password,
            is_active=data.is_active,
            balance=data.balance,
        )
        user = await use_case.execute(input_data)
        response = UserResponse.model_validate(user)
        
        logger.info({
            "action": "create_user",
            "stage": "end",
            "data": {"telegram_id": data.telegram_id, "success": True}
        })
        return response
    except ValueError as e:
        logger.error({
            "action": "create_user",
            "stage": "error",
            "data": {"telegram_id": data.telegram_id, "error": str(e)}
        })
        raise BadRequestException(detail=str(e))


@router.put(
    "/{telegram_id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
@inject
async def update_user(
    telegram_id: int,
    data: UserUpdate,
    use_case: UpdateUserUseCase = Depends(
        Provide[ApplicationContainer.update_user_use_case]
    ),
):
    """Обновить пользователя"""
    try:
        input_data = UpdateUserInput(
            telegram_id=telegram_id,
            password=data.password,
            is_active=data.is_active,
        )
        user = await use_case.execute(input_data)
        return UserResponse.model_validate(user)
    except UserNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{telegram_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_user(
    telegram_id: int,
    use_case: DeleteUserUseCase = Depends(
        Provide[ApplicationContainer.delete_user_use_case]
    ),
):
    """Удалить пользователя"""
    try:
        await use_case.execute(telegram_id)
    except UserNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/{telegram_id}/deposit",
    response_model=BalanceResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def deposit_balance(
    telegram_id: int,
    data: DepositRequest,
    use_case: DepositBalanceUseCase = Depends(
        Provide[ApplicationContainer.deposit_balance_use_case]
    ),
):
    """Пополнить баланс пользователя"""
    try:
        input_data = DepositInput(telegram_id=telegram_id, amount=data.amount)
        user = await use_case.execute(input_data)
        return BalanceResponse(
            telegram_id=user.telegram_id.value,
            balance=user.balance,
            updated_at=user.updated_at,
        )
    except UserNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))


@router.post(
    "/{telegram_id}/withdraw",
    response_model=BalanceResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def withdraw_balance(
    telegram_id: int,
    data: WithdrawRequest,
    use_case: WithdrawBalanceUseCase = Depends(
        Provide[ApplicationContainer.withdraw_balance_use_case]
    ),
):
    """Списать средства с баланса пользователя"""
    try:
        input_data = WithdrawInput(telegram_id=telegram_id, amount=data.amount)
        user = await use_case.execute(input_data)
        return BalanceResponse(
            telegram_id=user.telegram_id.value,
            balance=user.balance,
            updated_at=user.updated_at,
        )
    except UserNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))
