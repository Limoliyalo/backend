import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.transactions import Transaction
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.healthity.transactions import TransactionsRepository
from src.ports.repositories.healthity.users import UsersRepository


@dataclass
class CreateTransactionInput:
    user_tg_id: int
    amount: int
    type: str
    related_item_id: uuid.UUID | None = None
    related_background_id: uuid.UUID | None = None
    description: str | None = None


class CreateTransactionUseCase:
    def __init__(
        self,
        transactions_repository: TransactionsRepository,
        users_repository: UsersRepository,
    ) -> None:
        self._transactions_repository = transactions_repository
        self._users_repository = users_repository

    async def execute(self, data: CreateTransactionInput) -> Transaction:

        user = await self._users_repository.get_by_telegram_id(
            TelegramId(data.user_tg_id)
        )
        if user is None:
            raise EntityNotFoundException("User not found")

        if data.type == "deposit":
            new_balance = user.balance + data.amount
        elif data.type in [
            "purchase",
            "withdraw",
            "purchase_item",
            "purchase_background",
        ]:
            new_balance = user.balance - data.amount
        else:
            raise ValueError(
                "Invalid transaction type only deposit, purchase, withdraw, purchase_item, purchase_background are allowed"
            )

        if new_balance < 0:
            raise ValueError("Insufficient funds")

        user.balance = new_balance
        await self._users_repository.update(user)

        transaction = Transaction(
            id=uuid.uuid4(),
            user_tg_id=TelegramId(data.user_tg_id),
            amount=data.amount,
            balance_after=new_balance,
            type=data.type,
            related_item_id=data.related_item_id,
            related_background_id=data.related_background_id,
            description=data.description,
        )
        return await self._transactions_repository.add(transaction)


class GetTransactionUseCase:
    def __init__(self, transactions_repository: TransactionsRepository) -> None:
        self._transactions_repository = transactions_repository

    async def execute(self, transaction_id: uuid.UUID) -> Transaction:
        transaction = await self._transactions_repository.get(transaction_id)
        if transaction is None:
            raise EntityNotFoundException(f"Transaction {transaction_id} not found")
        return transaction


class ListTransactionsForUserUseCase:
    def __init__(self, transactions_repository: TransactionsRepository) -> None:
        self._transactions_repository = transactions_repository

    async def execute(self, user_tg_id: int) -> list[Transaction]:
        return await self._transactions_repository.list_for_user(TelegramId(user_tg_id))


@dataclass
class UpdateTransactionInput:
    transaction_id: uuid.UUID
    amount: int | None = None
    type: str | None = None
    description: str | None = None


class UpdateTransactionUseCase:
    def __init__(self, transactions_repository: TransactionsRepository) -> None:
        self._transactions_repository = transactions_repository

    async def execute(self, data: UpdateTransactionInput) -> Transaction:
        transaction = await self._transactions_repository.get(data.transaction_id)
        if transaction is None:
            raise EntityNotFoundException(
                f"Transaction {data.transaction_id} not found"
            )

        if data.amount is not None:
            transaction.amount = data.amount
        if data.type is not None:
            transaction.type = data.type
        if data.description is not None:
            transaction.description = data.description

        return await self._transactions_repository.update(transaction)


class DeleteTransactionUseCase:
    def __init__(self, transactions_repository: TransactionsRepository) -> None:
        self._transactions_repository = transactions_repository

    async def execute(self, transaction_id: uuid.UUID) -> None:
        transaction = await self._transactions_repository.get(transaction_id)
        if transaction is None:
            raise EntityNotFoundException(f"Transaction {transaction_id} not found")
        await self._transactions_repository.delete(transaction_id)
