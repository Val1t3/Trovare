"""Command and message handlers.

Each handler is a coroutine returning the text to send back to the user.
"""

import logging

from commands.help import handle_help
from commands.new import handle_new
from commands.registry import COMMANDS
from commands.params import CommandParameter
from llm.client import generate_reply
from llm.prompts import RESET_NOTICE, RESET_WARNING
from storage.context import append_turn, load_history, reset, should_reset, should_warn
from storage.models import ASSISTANT_AUTHOR, ContextMessage

logger = logging.getLogger(__name__)

COMMANDS["new"] = handle_new
COMMANDS["help"] = handle_help

_COMMANDS = COMMANDS


async def handle_command(command_name: str, params: CommandParameter) -> str:
    """Route a parsed "/command" to its handler in commands/."""
    handler = _COMMANDS.get(command_name.lower())
    if handler is None:
        return "Hello World!"
    return await handler(params)


async def handle_chat(text: str, author: str) -> str:
    """Handle free-text messages: call Haiku over the shared history, persist
    the turn, and append a proactive warning / auto-reset notice as needed."""
    history = await load_history()

    user_msg = ContextMessage(user=author, message=text)
    reply_text = await generate_reply(history + [user_msg])
    assistant_msg = ContextMessage(user=ASSISTANT_AUTHOR, message=reply_text)

    new_history = await append_turn(user_msg, assistant_msg)
    new_len = len(new_history)

    if should_reset(new_len):
        await reset()
        logger.info("Shared context auto-reset at %d messages", new_len)
        return reply_text + RESET_NOTICE
    if should_warn(new_len):
        return reply_text + RESET_WARNING
    return reply_text
