from abc import ABC, abstractmethod
import uuid

from src.domain.entities.healthity.transactions import Transaction
from src.domain.value_objects.telegram_id import TelegramId


class TransactionsRepository(ABC):
    @abstractmethod
    async def list_for_user(self, user_tg_id: TelegramId) -> list[Transaction]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, transaction: Transaction) -> Transaction:
        raise NotImplementedError

    @abstractmethod
    async def get(self, transaction_id: uuid.UUID) -> Transaction | None:
        raise NotImplementedError
