from fastapi import APIRouter
from models_api.models import ChatRequest, ChatResponse
from services import chat_service
from utils.logger import logger

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    logger(f"Received chat request: {request.message} in conversation {request.conversation_id}")
    return chat_service.process_chat(request.message, request.conversation_id)
