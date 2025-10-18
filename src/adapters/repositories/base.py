import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncIterator, Callable, Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.adapters.database.base import Base
from src.adapters.database.uow import AbstractUnitOfWork
from src.adapters.repositories.exceptions import (
    RepositoryError,
    IntegrityConstraintError,
    DuplicateEntityError,
)
from src.domain.exceptions import EntityNotFoundException

logger = logging.getLogger(__name__)

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

    def _make_datetime_naive(self, instance: ModelT) -> None:
        """Convert timezone-aware datetime fields to naive datetime"""
        for attr_name in dir(instance):
            if not attr_name.startswith("_"):
                try:
                    attr_value = getattr(instance, attr_name)
                    if (
                        isinstance(attr_value, datetime)
                        and attr_value.tzinfo is not None
                    ):
                        setattr(instance, attr_name, attr_value.replace(tzinfo=None))
                except (AttributeError, TypeError):

                    pass

    async def _check_entity_exists(
        self, model_class: type[Base], entity_id: Any, entity_name: str
    ) -> None:
        """Check if entity exists, raise EntityNotFoundException if not"""
        async with self._uow() as uow:
            entity = await uow.session.get(model_class, entity_id)
            if entity is None:
                raise EntityNotFoundException(f"{entity_name} not found")

    async def _validate_foreign_keys(self, instance: ModelT) -> None:
        """Validate foreign key constraints before adding instance"""

        pass

    async def add(self, instance: ModelT) -> ModelT:
        async with self._uow() as uow:
            logger.debug(f"Adding instance: {instance}")

            self._make_datetime_naive(instance)

            await self._validate_foreign_keys(instance)

            uow.session.add(instance)
            try:
                await uow.session.flush()
                await uow.session.refresh(instance)
                logger.debug(f"Successfully added instance: {instance}")
            except IntegrityError as exc:
                await uow.rollback()

                error_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
                logger.error(f"IntegrityError: {error_msg}")
                if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
                    logger.error(f"Duplicate entity detected: {error_msg}")
                    raise DuplicateEntityError("Entity already exists") from exc
                elif (
                    "check constraint" in error_msg.lower()
                    or "violates check" in error_msg.lower()
                ):
                    logger.error(f"Check constraint violated: {error_msg}")
                    raise IntegrityConstraintError(
                        "Invalid data: constraint violation"
                    ) from exc
                else:
                    logger.error(f"Integrity constraint violated: {error_msg}")
                    raise IntegrityConstraintError(
                        "Integrity constraint violated"
                    ) from exc
            except SQLAlchemyError as exc:
                await uow.rollback()

                if isinstance(exc, IntegrityError):
                    error_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
                    logger.error(f"IntegrityError in SQLAlchemyError: {error_msg}")
                    if (
                        "unique" in error_msg.lower()
                        or "duplicate" in error_msg.lower()
                    ):
                        logger.error(
                            f"Duplicate entity detected in SQLAlchemyError: {error_msg}"
                        )
                        raise DuplicateEntityError("Entity already exists") from exc
                    elif (
                        "check constraint" in error_msg.lower()
                        or "violates check" in error_msg.lower()
                    ):
                        logger.error(
                            f"Check constraint violated in SQLAlchemyError: {error_msg}"
                        )
                        raise IntegrityConstraintError(
                            "Invalid data: constraint violation"
                        ) from exc
                    else:
                        logger.error(
                            f"Integrity constraint violated in SQLAlchemyError: {error_msg}"
                        )
                        raise IntegrityConstraintError(
                            "Integrity constraint violated"
                        ) from exc
                else:
                    logger.error(f"SQLAlchemyError: {exc}")
                    raise RepositoryError("Database operation failed") from exc
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
