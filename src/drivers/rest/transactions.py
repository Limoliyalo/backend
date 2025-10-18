from datetime import datetime
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.core.auth.dependencies import get_access_token_payload
from src.core.auth.jwt_service import TokenPayload
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.transactions import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)
from src.ports.repositories.healthity.transactions import TransactionsRepository
from src.use_cases.transactions.manage_transactions import (
    CreateTransactionInput,
    CreateTransactionUseCase,
    DeleteTransactionUseCase,
    GetTransactionUseCase,
    ListTransactionsForUserUseCase,
    UpdateTransactionInput,
    UpdateTransactionUseCase,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/admin", response_model=list[TransactionResponse])
@inject
async def list_transactions(
    user_tg_id: int = Query(..., description="Telegram ID пользователя"),
    _: int = Depends(admin_user_provider),
    use_case: ListTransactionsForUserUseCase = Depends(
        Provide[ApplicationContainer.list_transactions_for_user_use_case]
    ),
):
    """Получить список транзакций пользователя (требуется админ-доступ)"""
    transactions = await use_case.execute(user_tg_id)
    return [TransactionResponse.model_validate(t) for t in transactions]


@router.get("/{transaction_id}/admin", response_model=TransactionResponse)
@inject
async def get_transaction(
    transaction_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: GetTransactionUseCase = Depends(
        Provide[ApplicationContainer.get_transaction_use_case]
    ),
):
    """Получить транзакцию по ID (требуется админ-доступ)"""
    try:
        transaction = await use_case.execute(transaction_id)
        return TransactionResponse.model_validate(transaction)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/admin", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_transaction(
    data: TransactionCreate,
    _: int = Depends(admin_user_provider),
    use_case: CreateTransactionUseCase = Depends(
        Provide[ApplicationContainer.create_transaction_use_case]
    ),
):
    """Создать новую транзакцию (требуется админ-доступ)"""
    input_data = CreateTransactionInput(
        user_tg_id=data.user_tg_id,
        amount=data.amount,
        type=data.type,
        related_item_id=data.related_item_id,
        related_background_id=data.related_background_id,
        description=data.description,
    )
    transaction = await use_case.execute(input_data)
    return TransactionResponse.model_validate(transaction)


@router.patch("/{transaction_id}/admin", response_model=TransactionResponse)
@inject
async def update_transaction(
    transaction_id: UUID,
    data: TransactionUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdateTransactionUseCase = Depends(
        Provide[ApplicationContainer.update_transaction_use_case]
    ),
):
    """Обновить транзакцию (требуется админ-доступ)"""
    try:
        input_data = UpdateTransactionInput(
            transaction_id=transaction_id,
            amount=data.amount,
            type=data.type,
            description=data.description,
        )
        transaction = await use_case.execute(input_data)
        return TransactionResponse.model_validate(transaction)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{transaction_id}/admin", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_transaction(
    transaction_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: DeleteTransactionUseCase = Depends(
        Provide[ApplicationContainer.delete_transaction_use_case]
    ),
):
    """Удалить транзакцию (требуется админ-доступ)"""
    try:
        await use_case.execute(transaction_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.get("/me", response_model=list[TransactionResponse])
@inject
async def list_my_transactions(
    start_date: datetime | None = Query(None, description="Начальная дата диапазона"),
    end_date: datetime | None = Query(None, description="Конечная дата диапазона"),
    transaction_type: str | None = Query(
        None,
        description="Тип транзакции (deposit, withdrawal, purchase_item, purchase_background)",
    ),
    payload: TokenPayload = Depends(get_access_token_payload),
    use_case: ListTransactionsForUserUseCase = Depends(
        Provide[ApplicationContainer.list_transactions_for_user_use_case]
    ),
    transactions_repo: TransactionsRepository = Depends(
        Provide[ApplicationContainer.transactions_repository]
    ),
):
    """Получить список транзакций текущего пользователя с фильтрацией

    Можно фильтровать по:
    - Диапазону дат (start_date, end_date)
    - Типу транзакции (transaction_type)
    Если фильтры не указаны, возвращаются все транзакции.
    """
    from src.domain.value_objects.telegram_id import TelegramId

    telegram_id = int(payload.sub)

    if start_date and end_date:
        transactions = await transactions_repo.list_for_user_by_date_range(
            TelegramId(telegram_id), start_date, end_date
        )
    elif transaction_type:
        transactions = await transactions_repo.list_for_user_by_type(
            TelegramId(telegram_id), transaction_type
        )
    else:
        transactions = await use_case.execute(telegram_id)

    return [TransactionResponse.model_validate(t) for t in transactions]
