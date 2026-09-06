"""
API route for the AI safety assistant.
"""
from fastapi import APIRouter, HTTPException

from app.models.scan import AssistantRequest, AssistantResponse
from app.services.assistant_service import ask_assistant

router = APIRouter(prefix="/assistant", tags=["Assistant"])


@router.post("/chat", response_model=AssistantResponse)
async def chat(request: AssistantRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")

    reply = await ask_assistant(request.message, request.scan_context)
    return AssistantResponse(reply=reply)