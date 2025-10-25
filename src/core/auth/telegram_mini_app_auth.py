import logging

from init_data_py import InitData
from init_data_py import errors as init_data_errors

from src.core.auth.schemas.tma import (
    TelegramAuthData,
    TelegramUser,
)
from src.domain.exceptions import InvalidTokenException
from src.domain.value_objects.telegram_id import TelegramId

logger = logging.getLogger(__name__)


class TelegramMiniAppAuth:
    """Telegram Mini App authentication service."""

    def __init__(self, bot_token: str):
        self.bot_token = bot_token

    def validate_init_data(self, init_data_raw: str) -> TelegramAuthData:
        try:
            init_data = InitData.parse(init_data_raw)
            init_data.validate(self.bot_token, lifetime=86400)

            # ---------- USER ----------
            user_obj = getattr(init_data, "user", None)
            user = None
            if user_obj is not None:
                user = TelegramUser(
                    id=user_obj.id,
                    first_name=getattr(user_obj, "first_name", None),
                    last_name=getattr(user_obj, "last_name", None),
                    username=getattr(user_obj, "username", None),
                    language_code=getattr(user_obj, "language_code", None),
                    is_premium=getattr(user_obj, "is_premium", None),
                    photo_url=getattr(user_obj, "photo_url", None),
                )

            # ---------- AUTH_DATE ----------
            auth_date = getattr(init_data, "auth_date", None)

            # В разных версиях lib сырьё называется raw / raw_data
            raw_data = getattr(init_data, "raw_data", None)
            if raw_data is None:
                raw_data = getattr(init_data, "raw", None)

            auth_data = TelegramAuthData(
                user=user,
                auth_date=auth_date,
                raw_data=raw_data,
            )

            logger.debug(
                "Successfully validated TMA init data",
                extra={"user_id": getattr(user, "id", None)},
            )
            return auth_data

        except (
            init_data_errors.SignMissingError,
            init_data_errors.AuthDateMissingError,
            init_data_errors.ExpiredError,
            init_data_errors.SignInvalidError,
            init_data_errors.UnexpectedFormatError,
        ) as exc:
            logger.warning(
                "TMA init data validation failed",
                extra={"error": str(exc)},
                exc_info=exc,
            )
            raise InvalidTokenException("Invalid Telegram Mini App init data") from exc
        except Exception as exc:
            logger.error(
                "Unexpected error during TMA validation",
                extra={"error": str(exc)},
                exc_info=exc,
            )
            raise InvalidTokenException(
                "Failed to validate Telegram Mini App data"
            ) from exc

    def get_telegram_id(self, auth_data: TelegramAuthData) -> TelegramId:
        """
        Extract Telegram ID from auth data.

        Args:
            auth_data: Validated Telegram auth data

        Returns:
            TelegramId: User's Telegram ID

        Raises:
            InvalidTokenException: If no user data found
        """
        if not auth_data.user:
            raise InvalidTokenException("No user data in Telegram Mini App init data")

        return TelegramId(auth_data.user.id)
