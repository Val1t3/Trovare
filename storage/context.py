"""Shared JSON-backed conversation context store.

Single global conversation (not per-channel), persisted under data/context.json,
which lives on the Docker-mounted ./data volume.
"""

import asyncio
import json
import logging
from pathlib import Path

from storage.models import ContextMessage

logger = logging.getLogger(__name__)

_CONTEXT_PATH = Path("data/context.json")

MAX_HISTORY = 20
WARNING_THRESHOLD = 15

_lock = asyncio.Lock()


def _read_sync() -> list[ContextMessage]:
    if not _CONTEXT_PATH.exists():
        return []
    try:
        raw = json.loads(_CONTEXT_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        logger.exception("Failed to read/parse %s; treating as empty", _CONTEXT_PATH)
        return []
    return [ContextMessage(user=item["user"], message=item["message"]) for item in raw]


def _write_sync(items: list[ContextMessage]) -> None:
    _CONTEXT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = [{"user": item.user, "message": item.message} for item in items]
    _CONTEXT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


async def load_history() -> list[ContextMessage]:
    """Return the current shared history, oldest first."""
    async with _lock:
        return await asyncio.to_thread(_read_sync)


async def append_turn(
    user_message: ContextMessage, assistant_message: ContextMessage
) -> list[ContextMessage]:
    """Append one user turn + one assistant turn, persist, and return the new history."""
    async with _lock:
        items = await asyncio.to_thread(_read_sync)
        items.append(user_message)
        items.append(assistant_message)
        await asyncio.to_thread(_write_sync, items)
        return items


async def reset() -> None:
    """Clear the shared history (used by /new and the auto-reset)."""
    async with _lock:
        await asyncio.to_thread(_write_sync, [])


def should_warn(history_len: int) -> bool:
    """True if the reply should carry a proactive "about to reset" warning.

    Each turn appends 2 entries, so the count only ever lands on even numbers
    right after a turn — a naive `== WARNING_THRESHOLD` check would never fire.
    Any length in [WARNING_THRESHOLD, MAX_HISTORY) triggers the warning.
    """
    return WARNING_THRESHOLD <= history_len < MAX_HISTORY


def should_reset(history_len: int) -> bool:
    """True if the history has reached the cap and must be auto-reset."""
    return history_len >= MAX_HISTORY
