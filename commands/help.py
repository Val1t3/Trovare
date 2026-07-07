"""/help — list available commands."""

from commands.params import CommandParameter
from commands.registry import COMMANDS, DESCRIPTIONS


async def handle_help(params: CommandParameter) -> str:
    """Display the list of available commands from the registry."""
    lines = [f"`/{cmd}` — {DESCRIPTIONS[cmd]}" for cmd in sorted(COMMANDS.keys())]
    return "**Commandes disponibles:**\n\n" + "\n".join(lines)
