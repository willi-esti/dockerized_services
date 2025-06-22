from fastapi import APIRouter
from models_api.models import ChatRequest, ChatResponse
from services import chat_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return chat_service.process_chat(request.message, request.conversation_id)
