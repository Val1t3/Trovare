"""FastAPI application entry point and Discord bot lifecycle."""

import asyncio
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from api.config import discord_bot_token, log_level
from api.routes import chat
from bot.discord_bot import create_client

load_dotenv()

logging.basicConfig(level=log_level())
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the Discord gateway client on startup, close it on exit."""
    token = discord_bot_token()
    client = None
    task = None

    if token:
        client = create_client()
        # Run the gateway connection in the background; awaiting it would block
        # the app from serving HTTP.
        task = asyncio.create_task(client.start(token))
    else:
        logger.warning("DISCORD_BOT_TOKEN not set; Discord disabled")
    app.state.discord_client = client
    try:
        yield
    finally:
        if client is not None:
            await client.close()
        if task is not None:
            try:
                await task
            except asyncio.CancelledError:
                pass


app = FastAPI(title="Trovare", lifespan=lifespan)
app.include_router(chat.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
