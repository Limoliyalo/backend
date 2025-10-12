from collections.abc import Callable
from datetime import datetime
import uuid

from sqlalchemy import delete, select

from src.adapters.database.models.transactions import TransactionModel
from src.adapters.database.uow import AbstractUnitOfWork
from src.adapters.repositories.base import SQLAlchemyRepository
from src.domain.entities.healthity.transactions import Transaction
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.healthity.transactions import TransactionsRepository


class SQLAlchemyTransactionsRepository(
    SQLAlchemyRepository[TransactionModel], TransactionsRepository
):
    model = TransactionModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def list_for_user(self, user_tg_id: TelegramId) -> list[Transaction]:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(TransactionModel)
                .where(TransactionModel.user_tg_id == user_tg_id.value)
                .order_by(TransactionModel.timestamp.desc())
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def list_for_user_by_date_range(
        self, user_tg_id: TelegramId, start_date: datetime, end_date: datetime
    ) -> list[Transaction]:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(TransactionModel)
                .where(
                    TransactionModel.user_tg_id == user_tg_id.value,
                    TransactionModel.timestamp >= start_date,
                    TransactionModel.timestamp <= end_date,
                )
                .order_by(TransactionModel.timestamp.desc())
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def list_for_user_by_type(
        self, user_tg_id: TelegramId, transaction_type: str
    ) -> list[Transaction]:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(TransactionModel)
                .where(
                    TransactionModel.user_tg_id == user_tg_id.value,
                    TransactionModel.type == transaction_type,
                )
                .order_by(TransactionModel.timestamp.desc())
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def add(self, transaction: Transaction) -> Transaction:
        model = TransactionModel(
            id=transaction.id,
            user_tg_id=transaction.user_tg_id.value,
            amount=transaction.amount,
            balance_after=transaction.balance_after,
            type=transaction.type,
            related_item_id=transaction.related_item_id,
            related_background_id=transaction.related_background_id,
            description=transaction.description,
            timestamp=transaction.timestamp,
        )
        saved_model = await super().add(model)
        return self._to_domain(saved_model)

    async def get(self, transaction_id: uuid.UUID) -> Transaction | None:
        model = await super().get(transaction_id)
        if model is None:
            return None
        return self._to_domain(model)

    async def update(self, transaction: Transaction) -> Transaction:
        async with self._uow() as uow:
            model = await uow.session.get(TransactionModel, transaction.id)
            if model is None:
                raise ValueError("Transaction not found")

            model.amount = transaction.amount
            model.type = transaction.type
            model.description = transaction.description

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    async def delete(self, transaction_id: uuid.UUID) -> None:
        async with self._uow() as uow:
            await uow.session.execute(
                delete(TransactionModel).where(TransactionModel.id == transaction_id)
            )

    @staticmethod
    def _to_domain(model: TransactionModel) -> Transaction:
        return Transaction(
            id=model.id,
            user_tg_id=TelegramId(model.user_tg_id),
            amount=model.amount,
            balance_after=model.balance_after,
            type=model.type,
            related_item_id=model.related_item_id,
            related_background_id=model.related_background_id,
            description=model.description,
            timestamp=model.timestamp,
        )
