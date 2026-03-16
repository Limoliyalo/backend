import logging

import httpx

from src.core.settings import settings

logger = logging.getLogger(__name__)

_TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}"


async def send_telegram_message(tg_id: int, text: str) -> None:
    """
    Send a text message to a Telegram user via the Bot API.

    tg_id is both the system user_id and the Telegram chat ID because
    the UserModel uses tg_id as its primary key.
    """
    url = f"{_TELEGRAM_API_BASE.format(token=settings.telegram_bot_token)}/sendMessage"
    payload = {"chat_id": tg_id, "text": text, "parse_mode": "HTML"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logger.info("Telegram message sent to user %s", tg_id)
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Telegram API error for user %s: %s — %s",
                tg_id,
                exc.response.status_code,
                exc.response.text,
            )
            raise
        except httpx.RequestError as exc:
            logger.error("Telegram request failed for user %s: %s", tg_id, exc)
            raise
