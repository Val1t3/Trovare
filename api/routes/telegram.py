"""POST /telegram — main Telegram webhook.

Receives updates, validates the sender, dispatches the message and replies.
"""

import logging

from fastapi import APIRouter, Request
from telegram import Bot, Update

from api.config import allowed_chat_ids
from bot.dispatcher import dispatch

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/telegram")
async def telegram_webhook(request: Request) -> dict[str, bool]:
    bot: Bot = request.app.state.bot
    payload = await request.json()
    update = Update.de_json(payload, bot)

    message = update.message or update.edited_message
    if message is None or message.text is None:
        # Nothing actionable (join events, media without caption, etc.).
        return {"ok": True}

    chat_id = message.chat_id

    # Security: only accept messages from allow-listed chats; reject silently.
    if chat_id not in allowed_chat_ids():
        logger.warning("Rejected update from unauthorized chat_id=%s", chat_id)
        return {"ok": True}

    reply = await dispatch(message.text)

    try:
        await bot.send_message(chat_id=chat_id, text=reply)
    except Exception:
        # In local simulation the token is a placeholder, so the send fails.
        # Log the reply so the flow is still verifiable without a real bot.
        logger.exception("Failed to send Telegram message; reply was: %r", reply)

    return {"ok": True}
