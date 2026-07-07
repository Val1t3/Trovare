"""Environment configuration helpers.

Secrets are read via os.getenv only and never logged.
"""

import logging
import os


def telegram_bot_token() -> str | None:
    """Telegram bot token from @BotFather."""
    return os.getenv("TELEGRAM_BOT_TOKEN")


def allowed_chat_ids() -> set[int]:
    """Parse TELEGRAM_ALLOWED_CHAT_IDS (comma-separated) into a set of ints."""
    raw = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "")
    ids: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.add(int(part))
        except ValueError:
            logging.warning("Ignoring invalid chat id in TELEGRAM_ALLOWED_CHAT_IDS")
    return ids


def log_level() -> str:
    """Logging level name (defaults to INFO)."""
    return os.getenv("LOG_LEVEL", "INFO").upper()


def port() -> int:
    """HTTP port (defaults to 8000)."""
    return int(os.getenv("PORT", "8000"))
