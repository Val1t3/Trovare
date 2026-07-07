"""POST /chat — conversational REST surface (also used to exercise the dispatcher)."""

from fastapi import APIRouter
from pydantic import BaseModel

from bot.dispatcher import dispatch

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    reply = await dispatch(request.message)
    return ChatResponse(reply=reply)
