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
    async def get_by_user(self, user_tg_id: TelegramId) -> Character | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, character: Character) -> Character:
        raise NotImplementedError

    @abstractmethod
    async def update(self, character: Character) -> Character:
        raise NotImplementedError


class CharacterItemsRepository(ABC):
    @abstractmethod
    async def list_for_character(self, character_id: uuid.UUID) -> list[CharacterItem]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, character_item: CharacterItem) -> CharacterItem:
        raise NotImplementedError

    @abstractmethod
    async def update(self, character_item: CharacterItem) -> CharacterItem:
        raise NotImplementedError


class CharacterBackgroundsRepository(ABC):
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
