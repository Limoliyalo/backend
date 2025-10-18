from collections.abc import Callable
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.adapters.database.models.catalog import (
    BackgroundModel,
    ItemCategoryModel,
    ItemModel,
)
from src.adapters.database.uow import AbstractUnitOfWork
from src.adapters.repositories.base import SQLAlchemyRepository
from src.adapters.repositories.exceptions import (
    RepositoryError,
    IntegrityConstraintError,
)
from src.domain.entities.healthity.catalog import Background, Item, ItemCategory
from src.ports.repositories.healthity.catalog import (
    BackgroundsRepository,
    ItemCategoriesRepository,
    ItemsRepository,
)


class SQLAlchemyItemCategoriesRepository(
    SQLAlchemyRepository[ItemCategoryModel], ItemCategoriesRepository
):
    model = ItemCategoryModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def list_all(self) -> list[ItemCategory]:
        models = await self.list()
        return [self._to_domain(model) for model in models]

    async def get_by_name(self, name: str) -> ItemCategory | None:
        model = await self.first(filters={"name": name})
        if model is None:
            return None
        return self._to_domain(model)

    async def get_by_id(self, category_id: uuid.UUID) -> ItemCategory | None:
        model = await super().get(category_id)
        if model is None:
            return None
        return self._to_domain(model)

    async def add(self, category: ItemCategory) -> ItemCategory:
        model = ItemCategoryModel(
            id=category.id,
            name=category.name,
            description=category.description,
            created_at=category.created_at,
        )
        saved_model = await super().add(model)
        return self._to_domain(saved_model)

    async def delete(self, category_id: uuid.UUID) -> None:
        async with self._uow() as uow:
            model = await uow.session.get(ItemCategoryModel, category_id)
            if model is None:
                raise RepositoryError("Item category not found")
            await uow.session.delete(model)

    @staticmethod
    def _to_domain(model: ItemCategoryModel) -> ItemCategory:
        return ItemCategory(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )


class SQLAlchemyItemsRepository(SQLAlchemyRepository[ItemModel], ItemsRepository):
    model = ItemModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def get(self, item_id: uuid.UUID) -> Item | None:
        model = await super().get(item_id)
        if model is None:
            return None
        return self._to_domain(model)

    async def list_by_category(self, category_id: uuid.UUID) -> list[Item]:
        models = await self.list(filters={"category_id": category_id})
        return [self._to_domain(model) for model in models]

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Item]:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(ItemModel).limit(limit).offset(offset)
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def list_available(self) -> list[Item]:
        models = await self.list(filters={"is_available": True})
        return [self._to_domain(model) for model in models]

    async def add(self, item: Item) -> Item:
        model = ItemModel(
            id=item.id,
            category_id=item.category_id,
            name=item.name,
            description=item.description,
            cost=item.cost,
            required_level=item.required_level,
            is_available=item.is_available,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        saved_model = await super().add(model)
        return self._to_domain(saved_model)

    async def update(self, item: Item) -> Item:
        async with self._uow() as uow:
            model = await uow.session.get(ItemModel, item.id)
            if model is None:
                raise RepositoryError("Item not found")

            model.category_id = item.category_id
            model.name = item.name
            model.description = item.description
            model.cost = item.cost
            model.required_level = item.required_level
            model.is_available = item.is_available

            try:
                await uow.session.flush()
                await uow.session.refresh(model)
                return self._to_domain(model)
            except IntegrityError as exc:
                await uow.rollback()
                error_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
                if (
                    "check constraint" in error_msg.lower()
                    or "violates check" in error_msg.lower()
                ):
                    raise IntegrityConstraintError(
                        "Invalid data: constraint violation"
                    ) from exc
                else:
                    raise IntegrityConstraintError(
                        "Integrity constraint violated"
                    ) from exc
            except SQLAlchemyError as exc:
                await uow.rollback()
                raise RepositoryError("Database operation failed") from exc

    async def delete(self, item_id: uuid.UUID) -> None:
        async with self._uow() as uow:
            model = await uow.session.get(ItemModel, item_id)
            if model is None:
                raise RepositoryError("Item not found")
            await uow.session.delete(model)

    @staticmethod
    def _to_domain(model: ItemModel) -> Item:
        return Item(
            id=model.id,
            category_id=model.category_id,
            name=model.name,
            description=model.description,
            cost=model.cost,
            required_level=model.required_level,
            is_available=model.is_available,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SQLAlchemyBackgroundsRepository(
    SQLAlchemyRepository[BackgroundModel], BackgroundsRepository
):
    model = BackgroundModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def get(self, background_id: uuid.UUID) -> Background | None:
        model = await super().get(background_id)
        if model is None:
            return None
        return self._to_domain(model)

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Background]:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(BackgroundModel).limit(limit).offset(offset)
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def list_available(self) -> list[Background]:
        models = await self.list(filters={"is_available": True})
        return [self._to_domain(model) for model in models]

    async def add(self, background: Background) -> Background:
        model = BackgroundModel(
            id=background.id,
            name=background.name,
            description=background.description,
            color=background.color,
            cost=background.cost,
            required_level=background.required_level,
            is_available=background.is_available,
            created_at=background.created_at,
        )
        saved_model = await super().add(model)
        return self._to_domain(saved_model)

    async def update(self, background: Background) -> Background:
        async with self._uow() as uow:
            model = await uow.session.get(BackgroundModel, background.id)
            if model is None:
                raise RepositoryError("Background not found")

            model.name = background.name
            model.description = background.description
            model.color = background.color
            model.cost = background.cost
            model.required_level = background.required_level
            model.is_available = background.is_available

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    async def delete(self, background_id: uuid.UUID) -> None:
        async with self._uow() as uow:
            model = await uow.session.get(BackgroundModel, background_id)
            if model is None:
                raise RepositoryError("Background not found")
            await uow.session.delete(model)

    @staticmethod
    def _to_domain(model: BackgroundModel) -> Background:
        return Background(
            id=model.id,
            name=model.name,
            description=model.description,
            color=model.color,
            cost=model.cost,
            required_level=model.required_level,
            is_available=model.is_available,
            created_at=model.created_at,
        )
