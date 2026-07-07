"""Dataclasses for stored conversation data."""

from dataclasses import dataclass

ASSISTANT_AUTHOR = "assistant"


@dataclass
class ContextMessage:
    """One turn in the shared conversation history, as persisted to JSON."""

    user: str
    message: str
