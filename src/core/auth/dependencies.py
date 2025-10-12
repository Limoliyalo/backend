"""FastAPI dependencies for authentication."""

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from src.container import ApplicationContainer
from src.core.auth.jwt_service import TokenPayload
from src.core.auth.providers import AccessTokenPayloadProvider, http_bearer


@inject
async def get_access_token_payload(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(http_bearer),
    ],
    provider: AccessTokenPayloadProvider = Depends(
        Provide[ApplicationContainer.access_token_payload_provider]
    ),
) -> TokenPayload:
    """Get and validate access token payload."""
    return await provider(credentials)
