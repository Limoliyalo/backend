from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.container import ApplicationContainer
from src.core.auth.admin import admin_user_provider
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.transactions import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)
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


@router.get("/admin/{transaction_id}", response_model=TransactionResponse)
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
        balance_after=0,  # Будет вычислен в use case
        type=data.type,
        related_item_id=data.related_item_id,
        related_background_id=data.related_background_id,
        description=data.description,
    )
    transaction = await use_case.execute(input_data)
    return TransactionResponse.model_validate(transaction)


@router.patch("/admin/{transaction_id}", response_model=TransactionResponse)
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


@router.delete("/admin/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
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
