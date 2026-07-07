"""Discord gateway client.

Listens to messages in the allow-listed channels, forwards their text to the
shared dispatcher and posts the reply back to the same channel.
"""

import logging

import discord

from api.config import allowed_channel_ids
from bot.dispatcher import dispatch

logger = logging.getLogger(__name__)

# Discord rejects messages longer than 2000 characters.
_MAX_MESSAGE_LEN = 2000


def create_client() -> discord.Client:
    """Build the Discord client wired to the on_message handler.

    Requires the privileged Message Content intent (also enable it in the
    Discord developer portal) so message text is readable.
    """
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:
        logger.info("Discord bot connected as %s", client.user)

    @client.event
    async def on_message(message: discord.Message) -> None:
        # Ignore our own messages to avoid feedback loops.
        if message.author == client.user:
            return

        # Security: only serve allow-listed channels; ignore silently.
        if message.channel.id not in allowed_channel_ids():
            logger.warning(
                "Ignored message from unauthorized channel_id=%s", message.channel.id
            )
            return

        if not message.content:
            return

        # Log every message forwarded to the app core.
        logger.info(
            "Message from author=%s channel_id=%s: %r",
            message.author,
            message.channel.id,
            message.content,
        )

        reply = await dispatch(message.content)

        # Log the reply sent back to the channel.
        logger.info("Reply to channel_id=%s: %r", message.channel.id, reply)

        try:
            await message.channel.send(reply[:_MAX_MESSAGE_LEN])
        except Exception:
            # Keep the flow verifiable even if sending fails (e.g. permissions).
            logger.exception("Failed to send Discord message; reply was: %r", reply)

    return client
