"""Message routing: map an incoming text to a handler and return its reply.

Pure async logic shared by the Discord bot and the REST /chat route.
"""

from bot.handlers import handle_chat, handle_command
from commands.params import CommandParameter


async def dispatch(text: str, author: str = "user") -> str:
    """Route an incoming message text to the right handler and return the reply.

    `author` is the display name of the human sender; it is recorded in the
    shared JSON context and used to disambiguate the two users when building
    the Claude messages array. Defaults to "user" for callers without a real
    Discord identity (e.g. the REST /chat route).
    """
    stripped = text.strip()
    if stripped.startswith("/"):
        parts = stripped[1:].split()
        command_name, args = (parts[0], parts[1:]) if parts else ("", [])
        return await handle_command(command_name, CommandParameter(author=author, args=args))
    return await handle_chat(stripped, author)
