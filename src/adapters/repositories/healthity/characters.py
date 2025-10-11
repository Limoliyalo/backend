from collections.abc import Callable
import uuid

from sqlalchemy import select

from src.adapters.database.models.characters import (
    CharacterBackgroundModel,
    CharacterItemModel,
    CharacterModel,
    ItemBackgroundPositionModel,
)
from src.adapters.database.uow import AbstractUnitOfWork
from src.adapters.repositories.base import SQLAlchemyRepository
from src.adapters.repositories.exceptions import RepositoryError
from src.domain.entities.healthity.characters import (
    Character,
    CharacterBackground,
    CharacterItem,
    ItemBackgroundPosition,
)
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.healthity.characters import (
    CharacterBackgroundsRepository,
    CharacterItemsRepository,
    CharactersRepository,
    ItemBackgroundPositionsRepository,
)


class SQLAlchemyCharactersRepository(
    SQLAlchemyRepository[CharacterModel], CharactersRepository
):
    model = CharacterModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def get_by_user(self, user_tg_id: TelegramId) -> Character | None:
        model = await self.first(filters={"user_tg_id": user_tg_id.value})
        if model is None:
            return None
        return self._to_domain(model)

    async def add(self, character: Character) -> Character:
        model = CharacterModel(
            id=character.id,
            user_tg_id=character.user_tg_id.value,
            name=character.name,
            sex=character.sex,
            current_mood=character.current_mood,
            level=character.level,
            total_experience=character.total_experience,
            created_at=character.created_at,
            updated_at=character.updated_at,
        )
        saved_model = await super().add(model)
        return self._to_domain(saved_model)

    async def update(self, character: Character) -> Character:
        async with self._uow() as uow:
            model = await uow.session.get(CharacterModel, character.id)
            if model is None:
                raise RepositoryError("Character not found")

            model.name = character.name
            model.sex = character.sex
            model.current_mood = character.current_mood
            model.level = character.level
            model.total_experience = character.total_experience

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    @staticmethod
    def _to_domain(model: CharacterModel) -> Character:
        return Character(
            id=model.id,
            user_tg_id=TelegramId(model.user_tg_id),
            name=model.name,
            sex=model.sex,
            current_mood=model.current_mood,
            level=model.level,
            total_experience=model.total_experience,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SQLAlchemyCharacterItemsRepository(
    SQLAlchemyRepository[CharacterItemModel], CharacterItemsRepository
):
    model = CharacterItemModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def list_for_character(self, character_id: uuid.UUID) -> list[CharacterItem]:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(CharacterItemModel).where(
                    CharacterItemModel.character_id == character_id
                )
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def add(self, character_item: CharacterItem) -> CharacterItem:
        model = CharacterItemModel(
            id=character_item.id,
            character_id=character_item.character_id,
            item_id=character_item.item_id,
            is_active=character_item.is_active,
            is_favourite=character_item.is_favourite,
            purchased_at=character_item.purchased_at,
        )
        saved_model = await super().add(model)
        return self._to_domain(saved_model)

    async def update(self, character_item: CharacterItem) -> CharacterItem:
        async with self._uow() as uow:
            model = await uow.session.get(CharacterItemModel, character_item.id)
            if model is None:
                raise RepositoryError("Character item not found")

            model.is_active = character_item.is_active
            model.is_favourite = character_item.is_favourite

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    @staticmethod
    def _to_domain(model: CharacterItemModel) -> CharacterItem:
        return CharacterItem(
            id=model.id,
            character_id=model.character_id,
            item_id=model.item_id,
            is_active=model.is_active,
            is_favourite=model.is_favourite,
            purchased_at=model.purchased_at,
        )


class SQLAlchemyCharacterBackgroundsRepository(
    SQLAlchemyRepository[CharacterBackgroundModel], CharacterBackgroundsRepository
):
    model = CharacterBackgroundModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def list_for_character(
        self, character_id: uuid.UUID
    ) -> list[CharacterBackground]:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(CharacterBackgroundModel).where(
                    CharacterBackgroundModel.character_id == character_id
                )
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def add(
        self, character_background: CharacterBackground
    ) -> CharacterBackground:
        model = CharacterBackgroundModel(
            id=character_background.id,
            character_id=character_background.character_id,
            background_id=character_background.background_id,
            is_active=character_background.is_active,
            is_favourite=character_background.is_favourite,
            purchased_at=character_background.purchased_at,
        )
        saved_model = await super().add(model)
        return self._to_domain(saved_model)

    async def update(
        self, character_background: CharacterBackground
    ) -> CharacterBackground:
        async with self._uow() as uow:
            model = await uow.session.get(
                CharacterBackgroundModel, character_background.id
            )
            if model is None:
                raise RepositoryError("Character background not found")

            model.is_active = character_background.is_active
            model.is_favourite = character_background.is_favourite

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    @staticmethod
    def _to_domain(model: CharacterBackgroundModel) -> CharacterBackground:
        return CharacterBackground(
            id=model.id,
            character_id=model.character_id,
            background_id=model.background_id,
            is_active=model.is_active,
            is_favourite=model.is_favourite,
            purchased_at=model.purchased_at,
        )


class SQLAlchemyItemBackgroundPositionsRepository(
    SQLAlchemyRepository[ItemBackgroundPositionModel],
    ItemBackgroundPositionsRepository,
):
    model = ItemBackgroundPositionModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def get(
        self, item_id: uuid.UUID, background_id: uuid.UUID
    ) -> ItemBackgroundPosition | None:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(ItemBackgroundPositionModel).where(
                    ItemBackgroundPositionModel.item_id == item_id,
                    ItemBackgroundPositionModel.background_id == background_id,
                )
            )
            model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def add(self, position: ItemBackgroundPosition) -> ItemBackgroundPosition:
        model = ItemBackgroundPositionModel(
            id=position.id,
            item_id=position.item_id,
            background_id=position.background_id,
            position_x=position.position_x,
            position_y=position.position_y,
            position_z=position.position_z,
        )
        saved_model = await super().add(model)
        return self._to_domain(saved_model)

    async def update(self, position: ItemBackgroundPosition) -> ItemBackgroundPosition:
        async with self._uow() as uow:
            model = await uow.session.get(ItemBackgroundPositionModel, position.id)
            if model is None:
                raise RepositoryError("Item background position not found")

            model.position_x = position.position_x
            model.position_y = position.position_y
            model.position_z = position.position_z

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    @staticmethod
    def _to_domain(model: ItemBackgroundPositionModel) -> ItemBackgroundPosition:
        return ItemBackgroundPosition(
            id=model.id,
            item_id=model.item_id,
            background_id=model.background_id,
            position_x=float(model.position_x),
            position_y=float(model.position_y),
            position_z=float(model.position_z),
        )
