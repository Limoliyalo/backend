from abc import ABC, abstractmethod
import uuid

from src.domain.entities.healthity.catalog import Background, Item, ItemCategory


class ItemCategoriesRepository(ABC):
    @abstractmethod
    async def get_by_id(self, category_id: uuid.UUID) -> ItemCategory | None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> list[ItemCategory]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, name: str) -> ItemCategory | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, category: ItemCategory) -> ItemCategory:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, category_id: uuid.UUID) -> None:
        raise NotImplementedError


class ItemsRepository(ABC):
    @abstractmethod
    async def get(self, item_id: uuid.UUID) -> Item | None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Item]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_category(self, category_id: uuid.UUID) -> list[Item]:
        raise NotImplementedError

    @abstractmethod
    async def list_available(self) -> list[Item]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, item: Item) -> Item:
        raise NotImplementedError

    @abstractmethod
    async def update(self, item: Item) -> Item:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, item_id: uuid.UUID) -> None:
        raise NotImplementedError


class BackgroundsRepository(ABC):
    @abstractmethod
    async def get(self, background_id: uuid.UUID) -> Background | None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Background]:
        raise NotImplementedError

    @abstractmethod
    async def list_available(self) -> list[Background]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, background: Background) -> Background:
        raise NotImplementedError

    @abstractmethod
    async def update(self, background: Background) -> Background:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, background_id: uuid.UUID) -> None:
        raise NotImplementedError
