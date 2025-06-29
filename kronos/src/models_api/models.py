from pydantic import BaseModel
from typing import List, Optional, Any

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    relevant_memory: Optional[List[dict]] = []
    confidence: Optional[str] = "medium"
    sources: Optional[List[str]] = []
    conversation_id: Optional[str] = None
    iterations: Optional[int] = 1
    action_taken: Optional[str] = "respond"
    reasoning: Optional[str] = ""

class MemoryRequest(BaseModel):
    text: str
    tags: Optional[List[str]] = None

class MemorySearchRequest(BaseModel):
    query: str
    top_k: int = 5

class TagRequest(BaseModel):
    item_id: str
    tag: str
