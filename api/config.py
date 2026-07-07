"""Environment configuration helpers.

Secrets are read via os.getenv only and never logged.
"""

import logging
import os


def discord_bot_token() -> str | None:
    """Discord bot token from the Discord developer portal."""
    return os.getenv("DISCORD_BOT_TOKEN")


def allowed_channel_ids() -> set[int]:
    """Parse DISCORD_ALLOWED_CHANNEL_IDS (comma-separated) into a set of ints."""
    raw = os.getenv("DISCORD_ALLOWED_CHANNEL_IDS", "")
    ids: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.add(int(part))
        except ValueError:
            logging.warning("Ignoring invalid channel id in DISCORD_ALLOWED_CHANNEL_IDS")
    return ids


def anthropic_api_key() -> str | None:
    """Anthropic API key (console.anthropic.com)."""
    return os.getenv("ANTHROPIC_API_KEY")


def anthropic_chat_model() -> str:
    """Model ID used for general chat (Haiku — fast/cheap)."""
    return os.getenv("ANTHROPIC_CHAT_MODEL", "claude-haiku-4-5-20251001")


def log_level() -> str:
    """Logging level name (defaults to INFO)."""
    return os.getenv("LOG_LEVEL", "INFO").upper()


def port() -> int:
    """HTTP port (defaults to 8000)."""
    return int(os.getenv("PORT", "8000"))
