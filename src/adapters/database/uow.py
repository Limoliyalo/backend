from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from typing import Awaitable, Self

from sqlalchemy.ext.asyncio import AsyncSession


class AbstractUnitOfWork(AbstractAsyncContextManager["AbstractUnitOfWork"], ABC):
    """Defines unit of work contract for SQLAlchemy repositories."""

    _session: AsyncSession | None
    _committed: bool

    def __init__(self) -> None:
        self._session = None
        self._committed = False

    @property
    def session(self) -> AsyncSession:
        if self._session is None:  # pragma: no cover - defensive branch
            raise RuntimeError("UnitOfWork session is not initialized")
        return self._session

    async def __aenter__(self) -> Self:
        self._session = await self._create_session()
        self._committed = False
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        try:
            if exc:
                await self.rollback()
            elif not self._committed:
                await self.commit()
        finally:
            await self.close()

    async def commit(self) -> None:
        await self.session.commit()
        self._committed = True

    async def rollback(self) -> None:
        if self._session is not None:
            await self._session.rollback()

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    @abstractmethod
    async def _create_session(
        self,
    ) -> AsyncSession:  # pragma: no cover - abstract method
        ...


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    """Unit of work implementation backed by an async session factory."""

    def __init__(
        self, session_factory: Callable[[], AsyncSession | Awaitable[AsyncSession]]
    ) -> None:
        super().__init__()
        self._session_factory = session_factory

    async def _create_session(self) -> AsyncSession:
        session_or_awaitable = self._session_factory()
        if hasattr(session_or_awaitable, "__await__"):
            return await session_or_awaitable  # type: ignore[return-value]
        if not isinstance(session_or_awaitable, AsyncSession):
            raise TypeError("Session factory must return an AsyncSession instance")
        return session_or_awaitable
