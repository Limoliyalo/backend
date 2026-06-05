"""Admin authentication and authorization."""

import logging
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.container import ApplicationContainer
from src.core.security import PasswordHasher
from src.drivers.rest.exceptions import ForbiddenException, UnauthorizedException
from src.ports.repositories.healthity.users import UsersRepository

logger = logging.getLogger(__name__)

security = HTTPBasic()


@inject
async def admin_user_provider(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    users_repository: UsersRepository = Depends(
        Provide[ApplicationContainer.users_repository]
    ),
    password_hasher: PasswordHasher = Depends(
        Provide[ApplicationContainer.password_hasher]
    ),
) -> int:
    try:
        telegram_id = int(credentials.username)
    except ValueError:
        logger.warning(
            {
                "action": "admin_auth",
                "stage": "invalid_username",
                "data": {"username_numeric": False},
            }
        )
        raise UnauthorizedException(
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    try:
        user = await users_repository.get_by_telegram_id(telegram_id)
    except Exception:
        logger.warning(
            {
                "action": "admin_auth",
                "stage": "user_not_found",
                "data": {"username_numeric": True},
            }
        )
        raise UnauthorizedException(
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    if user is None:
        logger.warning(
            {
                "action": "admin_auth",
                "stage": "user_not_found",
                "data": {"username_numeric": True},
            }
        )
        raise UnauthorizedException(
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not user.password_hash:
        logger.warning(
            {
                "action": "admin_auth",
                "stage": "no_password_set",
                "data": {"username_numeric": True},
            }
        )
        raise UnauthorizedException(
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not password_hasher.verify_password(credentials.password, user.password_hash):
        logger.warning(
            {
                "action": "admin_auth",
                "stage": "wrong_password",
                "data": {"username_numeric": True},
            }
        )
        raise UnauthorizedException(
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not user.is_admin:
        logger.warning(
            {
                "action": "admin_auth",
                "stage": "not_admin",
                "data": {"username_numeric": True},
            }
        )
        raise ForbiddenException(detail="Access denied: admin privileges required")

    logger.info(
        {
            "action": "admin_auth",
            "stage": "success",
            "data": {"username_numeric": True},
        }
    )
    return telegram_id
