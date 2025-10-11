from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Callable, Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.adapters.database.base import Base
from src.adapters.database.uow import AbstractUnitOfWork
from src.adapters.repositories.exceptions import RepositoryError


ModelT = TypeVar("ModelT", bound=Base)


class SQLAlchemyRepository(Generic[ModelT]):
    """Provides common helpers for repositories backed by SQLAlchemy models."""

    model: type[ModelT]

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        self._uow_factory = uow_factory

    @asynccontextmanager
    async def _uow(self) -> AsyncIterator[AbstractUnitOfWork]:
        async with self._uow_factory() as uow:
            yield uow

    async def add(self, instance: ModelT) -> ModelT:
        async with self._uow() as uow:
            uow.session.add(instance)
            try:
                await uow.session.flush()
            except IntegrityError as exc:  # pragma: no cover - DB constraint branch
                await uow.rollback()
                raise RepositoryError("Integrity constraint violated") from exc
            except SQLAlchemyError as exc:  # pragma: no cover - DB generic branch
                await uow.rollback()
                raise RepositoryError("Database operation failed") from exc
            await uow.session.refresh(instance)
            return instance

    async def create(self, **data: Any) -> ModelT:
        instance = self.model(**data)
        return await self.add(instance)

    async def get(self, entity_id: Any) -> ModelT | None:
        async with self._uow() as uow:
            return await uow.session.get(self.model, entity_id)

    async def delete(self, instance: ModelT) -> None:
        async with self._uow() as uow:
            await uow.session.delete(instance)

    async def list(
        self,
        /,
        *,
        filters: dict[str, Any] | None = None,
        statement: Select[tuple[ModelT]] | None = None,
    ) -> list[ModelT]:
        stmt = statement if statement is not None else select(self.model)
        if filters:
            stmt = stmt.filter_by(**filters)
        async with self._uow() as uow:
            result = await uow.session.execute(stmt)
            return list(result.scalars().all())

    async def first(
        self,
        /,
        *,
        filters: dict[str, Any] | None = None,
        statement: Select[tuple[ModelT]] | None = None,
    ) -> ModelT | None:
        stmt = statement if statement is not None else select(self.model)
        if filters:
            stmt = stmt.filter_by(**filters)
        async with self._uow() as uow:
            result = await uow.session.execute(stmt)
            return result.scalars().first()
