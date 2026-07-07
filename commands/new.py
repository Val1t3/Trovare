"""/new — reset the shared conversation context."""

from commands.params import CommandParameter
from storage.context import reset


async def handle_new(params: CommandParameter) -> str:
    """Reset the shared JSON history and confirm to the user."""
    await reset()
    return "Conversation réinitialisée. On repart de zéro !"
