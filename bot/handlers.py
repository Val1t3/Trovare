"""Command and message handlers.

Each handler is a coroutine returning the text to send back to the user.
Business logic (LLM, storage) will be wired in here later.
"""


async def handle_help() -> str:
    """Handle the /help command."""
    return "Hello World!"


async def handle_chat(text: str) -> str:
    """Handle free-text messages (placeholder until the LLM chat is wired in)."""
    return "Chat is not implemented yet."
