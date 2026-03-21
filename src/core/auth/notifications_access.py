"""API Key auth for /notifications/* (header: access-token)."""

import secrets

from fastapi import Depends
from fastapi.security import APIKeyHeader

from src.core.settings import settings
from src.drivers.rest.exceptions import UnauthorizedException

access_token_header = APIKeyHeader(name="access-token", auto_error=False)


async def verify_notifications_access_token(
    access_token: str | None = Depends(access_token_header),
) -> bool:
    if not settings.notifications_access_token:
        raise UnauthorizedException(
            detail="Notifications API is not configured (missing NOTIFICATIONS_ACCESS_TOKEN)",
        )
    if access_token is None:
        raise UnauthorizedException(detail="Missing access-token header")
    if not secrets.compare_digest(
        access_token.encode("utf-8"),
        settings.notifications_access_token.encode("utf-8"),
    ):
        raise UnauthorizedException(detail="Invalid access token")
    return True
