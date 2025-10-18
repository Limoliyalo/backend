from abc import ABC, abstractmethod
import uuid

from src.domain.entities.healthity.characters import (
    Character,
    CharacterBackground,
    CharacterItem,
    ItemBackgroundPosition,
)
from src.domain.value_objects.telegram_id import TelegramId


class CharactersRepository(ABC):
    @abstractmethod
    async def get_by_id(self, character_id: uuid.UUID) -> Character | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user(self, user_tg_id: TelegramId) -> Character | None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Character]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, character: Character) -> Character:
        raise NotImplementedError

    @abstractmethod
    async def update(self, character: Character) -> Character:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, character_id: uuid.UUID) -> None:
        raise NotImplementedError


class CharacterItemsRepository(ABC):
    @abstractmethod
    async def get_by_id(self, character_item_id: uuid.UUID) -> CharacterItem | None:
        raise NotImplementedError

    @abstractmethod
    async def list_for_character(self, character_id: uuid.UUID) -> list[CharacterItem]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, character_item: CharacterItem) -> CharacterItem:
        raise NotImplementedError

    @abstractmethod
    async def update(self, character_item: CharacterItem) -> CharacterItem:
        raise NotImplementedError

    @abstractmethod
    async def remove(self, character_item_id: uuid.UUID) -> None:
        raise NotImplementedError


class CharacterBackgroundsRepository(ABC):
    @abstractmethod
    async def get_by_id(
        self, character_background_id: uuid.UUID
    ) -> CharacterBackground | None:
        raise NotImplementedError

    @abstractmethod
    async def list_for_character(
        self, character_id: uuid.UUID
    ) -> list[CharacterBackground]:
        raise NotImplementedError

    @abstractmethod
    async def add(
        self, character_background: CharacterBackground
    ) -> CharacterBackground:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, character_background: CharacterBackground
    ) -> CharacterBackground:
        raise NotImplementedError

    @abstractmethod
    async def remove(self, character_background_id: uuid.UUID) -> None:
        raise NotImplementedError


class ItemBackgroundPositionsRepository(ABC):
    @abstractmethod
    async def get(
        self, item_id: uuid.UUID, background_id: uuid.UUID
    ) -> ItemBackgroundPosition | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, position: ItemBackgroundPosition) -> ItemBackgroundPosition:
        raise NotImplementedError

    @abstractmethod
    async def update(self, position: ItemBackgroundPosition) -> ItemBackgroundPosition:
        raise NotImplementedError
