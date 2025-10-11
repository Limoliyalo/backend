from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.container import ApplicationContainer
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.transactions import TransactionCreate, TransactionResponse
from src.use_cases.transactions.manage_transactions import (
    CreateTransactionInput,
    CreateTransactionUseCase,
    GetTransactionUseCase,
    ListTransactionsForUserUseCase,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/user/{user_tg_id}", response_model=list[TransactionResponse])
@inject
async def list_transactions_for_user(
    user_tg_id: int,
    use_case: ListTransactionsForUserUseCase = Depends(
        Provide[ApplicationContainer.list_transactions_for_user_use_case]
    ),
):
    """Получить транзакции пользователя"""
    transactions = await use_case.execute(user_tg_id)
    return [TransactionResponse.model_validate(t) for t in transactions]


@router.get("/{transaction_id}", response_model=TransactionResponse)
@inject
async def get_transaction(
    transaction_id: UUID,
    use_case: GetTransactionUseCase = Depends(
        Provide[ApplicationContainer.get_transaction_use_case]
    ),
):
    """Получить транзакцию по ID"""
    try:
        transaction = await use_case.execute(transaction_id)
        return TransactionResponse.model_validate(transaction)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_transaction(
    data: TransactionCreate,
    use_case: CreateTransactionUseCase = Depends(
        Provide[ApplicationContainer.create_transaction_use_case]
    ),
):
    """Создать новую транзакцию"""
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
