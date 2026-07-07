"""FastAPI application entry point and Telegram bot lifecycle."""

import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from telegram import Bot

from api.config import log_level, telegram_bot_token
from api.routes import chat, telegram

load_dotenv()

logging.basicConfig(level=log_level())
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the Telegram Bot on startup, shut it down on exit."""
    token = telegram_bot_token()
    bot = Bot(token) if token else None
    if bot is not None:
        try:
            await bot.initialize()
        except Exception:
            logger.exception("Telegram bot initialization failed; running degraded")
    else:
        logger.warning("TELEGRAM_BOT_TOKEN not set; Telegram sending disabled")
    app.state.bot = bot
    try:
        yield
    finally:
        if bot is not None:
            await bot.shutdown()


app = FastAPI(title="Trovare", lifespan=lifespan)
app.include_router(telegram.router)
app.include_router(chat.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
