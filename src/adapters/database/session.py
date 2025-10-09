from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.settings import settings


class SessionManager:
    """Класс, предоставляющий сессии для проекта."""

    def __init__(
        self,
        db_dsn: str,
        echo: bool = False,
        pool_size: int | None = None,
        max_overflow: int | None = None,
        pool_timeout: int | None = None,
    ):
        engine_kwargs: dict[str, object] = {
            "echo": echo,
            "pool_pre_ping": True,
        }

        if pool_size is not None:
            engine_kwargs["pool_size"] = pool_size

        if max_overflow is not None:
            engine_kwargs["max_overflow"] = max_overflow

        if pool_timeout is not None:
            engine_kwargs["pool_timeout"] = pool_timeout

        self.engine = create_async_engine(
            url=db_dsn,
            **engine_kwargs,
        )

    @property
    def async_session(self) -> async_sessionmaker[AsyncSession]:
        return self.create_session_factory()

    def create_session_factory(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def close(self) -> None:
        await self.engine.dispose()


session_manager = SessionManager(
    db_dsn=settings.database.async_url,
    echo=settings.database.echo,
)
