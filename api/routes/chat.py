"""POST /chat — conversational REST surface."""

from fastapi import APIRouter
from pydantic import BaseModel

from bot.dispatcher import dispatch

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    author: str = "user"


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    reply = await dispatch(request.message, author=request.author)
    return ChatResponse(reply=reply)
