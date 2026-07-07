"""Anthropic API wiring for general chat (Haiku)."""

from logging import Logger

from anthropic import AsyncAnthropic

from api.config import anthropic_api_key, anthropic_chat_model
from llm.prompts import SYSTEM_PROMPT
from storage.models import ASSISTANT_AUTHOR, ContextMessage

_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=anthropic_api_key())
    return _client


def _to_api_messages(history: list[ContextMessage]) -> list[dict[str, str]]:
    """Convert stored ContextMessage entries into Anthropic Messages API turns.

    The API only knows "user"/"assistant" roles. Assistant's own past replies
    map to role="assistant" verbatim. Every human author (both of the 2 users)
    maps to role="user", with their display name prefixed onto the content so
    Claude can still tell the two users apart within one shared thread, e.g.
    "Alice: quel est le loyer max ?".
    """
    messages: list[dict[str, str]] = []
    for item in history:
        if item.user == ASSISTANT_AUTHOR:
            messages.append({"role": "assistant", "content": item.message})
        else:
            messages.append({"role": "user", "content": f"{item.user}: {item.message}"})
    return messages


async def generate_reply(history: list[ContextMessage]) -> str:
    """Call Haiku with the full shared history (already includes the latest
    user turn) and return the assistant's reply text."""
    client = _get_client()
    response = await client.messages.create(
        model=anthropic_chat_model(),
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=_to_api_messages(history),
    )
    return "".join(block.text for block in response.content if block.type == "text")
