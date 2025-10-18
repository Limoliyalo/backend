import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.core.auth.dependencies import get_access_token_payload
from src.core.auth.jwt_service import TokenPayload
from src.domain.exceptions import EntityNotFoundException, UserNotFoundException
from src.domain.value_objects.telegram_id import TelegramId
from src.adapters.repositories.exceptions import RepositoryError, DuplicateEntityError
from src.drivers.rest.exceptions import BadRequestException, NotFoundException
from src.drivers.rest.schemas.users import (
    BalanceResponse,
    ChangePasswordRequest,
    DepositRequest,
    UserCreate,
    UserRegister,
    UserResponse,
    UserStatisticsResponse,
    UserUpdate,
    WithdrawRequest,
)
from src.ports.repositories.healthity.activities import MoodHistoryRepository
from src.ports.repositories.healthity.characters import (
    CharacterBackgroundsRepository,
    CharacterItemsRepository,
)
from src.ports.repositories.healthity.transactions import TransactionsRepository
from src.ports.repositories.healthity.users import UserFriendsRepository
from src.use_cases.characters.get_character import GetCharacterByUserUseCase
from src.use_cases.users.manage_users import (
    ChangePasswordInput,
    ChangePasswordUseCase,
    CreateUserInput,
    CreateUserUseCase,
    DeleteUserUseCase,
    DepositInput,
    DepositUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserInput,
    UpdateUserUseCase,
    WithdrawInput,
    WithdrawUseCase,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def register_user(
    data: UserRegister,
    use_case: CreateUserUseCase = Depends(
        Provide[ApplicationContainer.create_user_use_case]
    ),
):
    """Публичная регистрация пользователя (только telegram_id и пароль)"""
    logger.info(
        {
            "action": "register_user",
            "stage": "start",
            "data": {"telegram_id": data.telegram_id},
        }
    )

    try:
        input_data = CreateUserInput(
            telegram_id=data.telegram_id,
            password=data.password,
            is_active=True,
            balance=0,
        )
        user = await use_case.execute(input_data)
        response = UserResponse.model_validate(user)

        logger.info(
            {
                "action": "register_user",
                "stage": "end",
                "data": {"telegram_id": data.telegram_id, "success": True},
            }
        )
        return response
    except DuplicateEntityError:
        logger.error(
            {
                "action": "register_user",
                "stage": "error",
                "data": {
                    "telegram_id": data.telegram_id,
                    "error": "User already exists",
                },
            }
        )
        raise BadRequestException(detail="User already exists")
    except RepositoryError as e:
        logger.error(
            {
                "action": "register_user",
                "stage": "error",
                "data": {"telegram_id": data.telegram_id, "error": str(e)},
            }
        )
        raise BadRequestException(detail=str(e))
    except ValueError as e:
        logger.error(
            {
                "action": "register_user",
                "stage": "error",
                "data": {"telegram_id": data.telegram_id, "error": str(e)},
            }
        )
        raise BadRequestException(detail=str(e))


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
    "/{telegram_id}/admin", response_model=UserResponse, status_code=status.HTTP_200_OK
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
    except RepositoryError as e:
        logger.error(
            {
                "action": "create_user",
                "stage": "error",
                "data": {"telegram_id": data.telegram_id, "error": str(e)},
            }
        )
        raise BadRequestException(detail=str(e))
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
    "/{telegram_id}/admin", response_model=UserResponse, status_code=status.HTTP_200_OK
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


@router.delete("/{telegram_id}/admin", status_code=status.HTTP_204_NO_CONTENT)
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


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
@inject
async def get_current_user(
    payload: TokenPayload = Depends(get_access_token_payload),
    use_case: GetUserUseCase = Depends(Provide[ApplicationContainer.get_user_use_case]),
):
    """Получить информацию о текущем пользователе"""
    telegram_id = int(payload.sub)
    try:
        user = await use_case.execute(telegram_id)
        return UserResponse.model_validate(user)
    except UserNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/me/deposit", response_model=BalanceResponse, status_code=status.HTTP_200_OK
)
@inject
async def deposit(
    data: DepositRequest,
    payload: TokenPayload = Depends(get_access_token_payload),
    use_case: DepositUseCase = Depends(Provide[ApplicationContainer.deposit_use_case]),
):
    """Пополнить баланс текущего пользователя"""
    telegram_id = int(payload.sub)
    try:
        input_data = DepositInput(
            telegram_id=telegram_id,
            amount=data.amount,
            description=None,
        )
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
    "/me/withdraw", response_model=BalanceResponse, status_code=status.HTTP_200_OK
)
@inject
async def withdraw(
    data: WithdrawRequest,
    payload: TokenPayload = Depends(get_access_token_payload),
    use_case: WithdrawUseCase = Depends(
        Provide[ApplicationContainer.withdraw_use_case]
    ),
):
    """Списать средства с баланса текущего пользователя"""
    telegram_id = int(payload.sub)
    try:
        input_data = WithdrawInput(
            telegram_id=telegram_id,
            amount=data.amount,
            description=None,
        )
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


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def change_password(
    data: ChangePasswordRequest,
    payload: TokenPayload = Depends(get_access_token_payload),
    use_case: ChangePasswordUseCase = Depends(
        Provide[ApplicationContainer.change_password_use_case]
    ),
):
    """Изменить пароль текущего пользователя"""
    telegram_id = int(payload.sub)
    try:
        input_data = ChangePasswordInput(
            telegram_id=telegram_id,
            old_password=data.old_password,
            new_password=data.new_password,
        )
        await use_case.execute(input_data)
    except UserNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))


@router.get(
    "/me/statistics",
    response_model=UserStatisticsResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_my_statistics(
    payload: TokenPayload = Depends(get_access_token_payload),
    get_user_use_case: GetUserUseCase = Depends(
        Provide[ApplicationContainer.get_user_use_case]
    ),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    items_repo: CharacterItemsRepository = Depends(
        Provide[ApplicationContainer.character_items_repository]
    ),
    backgrounds_repo: CharacterBackgroundsRepository = Depends(
        Provide[ApplicationContainer.character_backgrounds_repository]
    ),
    mood_repo: MoodHistoryRepository = Depends(
        Provide[ApplicationContainer.mood_history_repository]
    ),
    transactions_repo: TransactionsRepository = Depends(
        Provide[ApplicationContainer.transactions_repository]
    ),
    friends_repo: UserFriendsRepository = Depends(
        Provide[ApplicationContainer.user_friends_repository]
    ),
):
    """Получить статистику текущего пользователя"""

    telegram_id = int(payload.sub)
    try:

        user = await get_user_use_case.execute(telegram_id)

        try:
            character = await get_character_use_case.execute(telegram_id)
            character_name = character.name
            character_sex = character.sex
            level = character.level
            total_experience = character.total_experience
            character_id = character.id
        except EntityNotFoundException:
            character_name = None
            character_sex = None
            level = None
            total_experience = None
            character_id = None

        if character_id:
            purchased_items = await items_repo.list_for_character(character_id)
            purchased_backgrounds = await backgrounds_repo.list_for_character(
                character_id
            )
            mood_entries = await mood_repo.list_for_character(character_id, limit=10000)
        else:
            purchased_items = []
            purchased_backgrounds = []
            mood_entries = []

        transactions = await transactions_repo.list_for_user(TelegramId(telegram_id))
        friends = await friends_repo.list_for_user(telegram_id)

        activities_count = len(mood_entries)

        return UserStatisticsResponse(
            user_id=telegram_id,
            balance=user.balance,
            level=level,
            total_experience=total_experience,
            character_name=character_name,
            character_sex=character_sex,
            purchased_items_count=len(purchased_items),
            purchased_backgrounds_count=len(purchased_backgrounds),
            mood_entries_count=len(mood_entries),
            activities_count=activities_count,
            total_transactions=len(transactions),
            friends_count=len(friends),
        )
    except UserNotFoundException as e:
        raise NotFoundException(detail=str(e))
