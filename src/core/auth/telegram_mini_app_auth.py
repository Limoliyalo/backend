import logging

from init_data_py import InitData
from init_data_py import errors as init_data_errors

from src.core.auth.schemas.tma import (
    TelegramAuthData,
    TelegramUser,
    TelegramChat,
    TelegramChatMember,
)
from src.domain.exceptions import InvalidTokenException
from src.domain.value_objects.telegram_id import TelegramId

logger = logging.getLogger(__name__)


class TelegramMiniAppAuth:
    """Telegram Mini App authentication service."""

    def __init__(self, bot_token: str):
        self.bot_token = bot_token

    def validate_init_data(self, init_data_raw: str) -> TelegramAuthData:
        """
        Validate Telegram Mini App init data and return parsed data.

        Args:
            init_data_raw: Raw init data string from Authorization header

        Returns:
            TelegramAuthData: Parsed and validated data

        Raises:
            InvalidTokenException: If validation fails
        """
        try:
            # Parse the init data
            init_data = InitData.parse(init_data_raw)

            # Validate the init data
            init_data.validate(self.bot_token)

            # Extract user data
            user = None
            if init_data.user:
                user = TelegramUser(
                    id=init_data.user.id,
                    first_name=init_data.user.first_name,
                    last_name=init_data.user.last_name,
                    username=init_data.user.username,
                    language_code=init_data.user.language_code,
                    is_premium=getattr(init_data.user, "is_premium", None),
                    photo_url=getattr(init_data.user, "photo_url", None),
                )

            # Extract chat data
            chat = None
            if init_data.chat:
                chat = TelegramChat(
                    id=init_data.chat.id,
                    type=init_data.chat.type,
                    title=getattr(init_data.chat, "title", None),
                    username=getattr(init_data.chat, "username", None),
                    photo_url=getattr(init_data.chat, "photo_url", None),
                )

            # Extract chat member data
            chat_member = None
            if init_data.chat_member:
                chat_member_user = None
                if init_data.chat_member.user:
                    chat_member_user = TelegramUser(
                        id=init_data.chat_member.user.id,
                        first_name=init_data.chat_member.user.first_name,
                        last_name=init_data.chat_member.user.last_name,
                        username=init_data.chat_member.user.username,
                        language_code=init_data.chat_member.user.language_code,
                        is_premium=getattr(
                            init_data.chat_member.user, "is_premium", None
                        ),
                        photo_url=getattr(
                            init_data.chat_member.user, "photo_url", None
                        ),
                    )

                chat_member = TelegramChatMember(
                    status=init_data.chat_member.status,
                    user=chat_member_user,
                    is_anonymous=getattr(init_data.chat_member, "is_anonymous", None),
                    custom_title=getattr(init_data.chat_member, "custom_title", None),
                )

            # Create auth data object
            auth_data = TelegramAuthData(
                user=user,
                chat=chat,
                chat_member=chat_member,
                chat_type=getattr(init_data, "chat_type", None),
                auth_date=getattr(init_data, "auth_date", None),
                start_param=getattr(init_data, "start_param", None),
                can_send_after=getattr(init_data, "can_send_after", None),
                raw_data=init_data.raw_data if hasattr(init_data, "raw_data") else None,
            )

            logger.debug(
                "Successfully validated TMA init data",
                extra={
                    "user_id": user.id if user else None,
                    "chat_id": chat.id if chat else None,
                },
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
