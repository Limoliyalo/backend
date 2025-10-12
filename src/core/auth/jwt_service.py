import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from jose import JWTError, jwt

from src.core.settings import settings
from src.domain.exceptions import InvalidTokenException, TokenExpiredException

logger = logging.getLogger(__name__)


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass
class TokenPayload:
    sub: str
    jti: UUID
    token_type: TokenType
    expires_at: datetime
    issued_at: datetime
    claims: dict[str, Any]


class JwtService:
    def __init__(self) -> None:
        jwt_settings = settings.jwt
        self._secret_key = jwt_settings.secret_key
        self._algorithm = jwt_settings.algorithm
        self._access_ttl = timedelta(minutes=jwt_settings.access_token_expire_minutes)
        self._refresh_ttl = timedelta(minutes=jwt_settings.refresh_token_expire_minutes)

    def create_access_token(
        self, *, subject: str | int, additional_claims: dict[str, Any] | None = None
    ) -> tuple[str, datetime, UUID]:
        return self._create_token(
            subject=subject,
            token_type=TokenType.ACCESS,
            expires_delta=self._access_ttl,
            additional_claims=additional_claims,
        )

    def create_refresh_token(
        self, *, subject: str | int, additional_claims: dict[str, Any] | None = None
    ) -> tuple[str, datetime, UUID]:
        return self._create_token(
            subject=subject,
            token_type=TokenType.REFRESH,
            expires_delta=self._refresh_ttl,
            additional_claims=additional_claims,
        )

    def decode(
        self, token: str, *, expected_type: TokenType | None = None
    ) -> TokenPayload:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except JWTError as exc:
            logger.debug("Failed to decode token", exc_info=exc)
            raise InvalidTokenException() from exc

        token_type = payload.get("type")
        if token_type is None:
            raise InvalidTokenException("Missing token type")

        try:
            parsed_type = TokenType(token_type)
        except ValueError as exc:
            raise InvalidTokenException("Unknown token type") from exc

        if expected_type and parsed_type is not expected_type:
            raise InvalidTokenException("Unexpected token type")

        exp_ts = payload.get("exp")
        if exp_ts is None:
            raise InvalidTokenException("Missing exp claim")

        exp = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        if exp < now:
            raise TokenExpiredException()

        jti_value = payload.get("jti")
        if jti_value is None:
            raise InvalidTokenException("Missing jti claim")

        issued_at_ts = payload.get("iat")
        if issued_at_ts is None:
            raise InvalidTokenException("Missing iat claim")

        claims: dict[str, Any] = dict(payload)

        return TokenPayload(
            sub=str(payload.get("sub")),
            jti=UUID(str(jti_value)),
            token_type=parsed_type,
            expires_at=exp,
            issued_at=datetime.fromtimestamp(issued_at_ts, tz=timezone.utc),
            claims=claims,
        )

    def _create_token(
        self,
        *,
        subject: str | int,
        token_type: TokenType,
        expires_delta: timedelta,
        additional_claims: dict[str, Any] | None = None,
    ) -> tuple[str, datetime, UUID]:
        now = datetime.now(tz=timezone.utc)
        expire = now + expires_delta
        jti = uuid4()

        payload: dict[str, Any] = {
            "sub": str(subject),
            "jti": str(jti),
            "type": token_type.value,
            "iat": int(now.timestamp()),
            "nbf": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }

        if additional_claims:
            payload.update(additional_claims)

        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return token, expire, jti
