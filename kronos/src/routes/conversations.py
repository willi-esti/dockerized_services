from fastapi import APIRouter
from services import conversation_service
from typing import Optional

router = APIRouter()

@router.get("/conversations")
def get_conversations(tag: Optional[str] = None, time: Optional[str] = None):
    return conversation_service.get_all_conversations(tag, time)

@router.get("/conversations/{id}")
def get_conversation(id: str):
    return conversation_service.get_conversation_by_id(id)
