from fastapi import APIRouter, Query
from services import conversation_service
from typing import Optional

router = APIRouter(prefix="/api/v1")

@router.get("/conversations")
def get_conversations(
    tag: Optional[str] = None, 
    time: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """Get list of conversations with pagination."""
    return conversation_service.get_all_conversations(tag, time, limit, offset)

@router.get("/conversations/{id}")
def get_conversation(id: str):
    """Get a specific conversation with all messages."""
    conversation = conversation_service.get_conversation_by_id(id)
    if not conversation:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation
