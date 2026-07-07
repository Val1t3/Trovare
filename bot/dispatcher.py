"""Message routing: map an incoming text to a handler and return its reply.

Pure async logic shared by the Discord bot and the REST /chat route.
Later this will delegate free text to the Haiku intent classifier.
"""

from bot.handlers import handle_chat, handle_help


async def dispatch(text: str) -> str:
    """Route an incoming message text to the right handler and return the reply."""
    stripped = text.strip()
    if stripped.startswith("/help"):
        return await handle_help()
    return await handle_chat(stripped)
