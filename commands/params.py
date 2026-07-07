"""Shared argument type for command handlers."""

from dataclasses import dataclass


@dataclass
class CommandParameter:
    """Single argument passed to every command handler.

    All fields are optional so new commands can add fields without breaking
    the shared handler signature `async def handle_x(params: CommandParameter) -> str`.
    """

    author: str | None = None
    args: list[str] | None = None
