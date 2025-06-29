from fastapi import APIRouter
from models_api.models import ChatRequest, ChatResponse
from services import chat_service
from services.ollama_service import ollama_service
from config.logger import logger

router = APIRouter(prefix="/api/v1")

@router.post("/chat/send", response_model=ChatResponse)
def chat(request: ChatRequest):
    logger(f"Received chat request: {request.message} in conversation {request.conversation_id}")
    return chat_service.process_chat(request.message, request.conversation_id)

@router.get("/ollama/status")
def ollama_status():
    """Check if Ollama is available."""
    is_available = ollama_service.is_available()
    models = ollama_service.list_models() if is_available else []
    
    return {
        "available": is_available,
        "models": models,
        "url": ollama_service.ollama_url
    }
