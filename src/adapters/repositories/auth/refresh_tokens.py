from collections.abc import Callable
from uuid import UUID

from sqlalchemy import update

from src.adapters.database.models.refresh_token import RefreshTokenModel
from src.adapters.database.uow import AbstractUnitOfWork
from src.adapters.repositories.base import SQLAlchemyRepository
from src.domain.entities.auth import RefreshToken
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.auth import RefreshTokensRepository


class SQLAlchemyRefreshTokensRepository(
    SQLAlchemyRepository[RefreshTokenModel], RefreshTokensRepository
):
    model = RefreshTokenModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def create(self, token: RefreshToken) -> RefreshToken:
        model = RefreshTokenModel(
            id=token.id,
            user_tg_id=token.user_tg_id.value,
            token_hash=token.token_hash,
            jti=token.jti,
            expires_at=token.expires_at,
            revoked=token.revoked,
        )
        saved = await self.add(model)
        return self._to_domain(saved)

    async def get_by_jti(self, jti: UUID) -> RefreshToken | None:
        model = await self.first(filters={"jti": jti})
        if model is None:
            return None
        return self._to_domain(model)

    async def save(self, token: RefreshToken) -> RefreshToken:
        async with self._uow() as uow:
            model = await uow.session.get(RefreshTokenModel, token.id)
            if model is None:
                raise ValueError("RefreshToken not found")

            model.token_hash = token.token_hash
            model.expires_at = token.expires_at
            model.revoked = token.revoked

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    async def revoke_for_user(self, user_tg_id: TelegramId) -> None:
        async with self._uow() as uow:
            await uow.session.execute(
                update(RefreshTokenModel)
                .where(RefreshTokenModel.user_tg_id == user_tg_id.value)
                .values(revoked=True)
            )

    @staticmethod
    def _to_domain(model: RefreshTokenModel) -> RefreshToken:
        return RefreshToken(
            id=model.id,
            user_tg_id=TelegramId(model.user_tg_id),
            token_hash=model.token_hash,
            jti=model.jti,
            expires_at=model.expires_at,
            revoked=model.revoked,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
