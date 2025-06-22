from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    relevant_memory: List[dict]

class MemoryRequest(BaseModel):
    text: str
    tags: Optional[List[str]] = None

class MemorySearchRequest(BaseModel):
    query: str
    top_k: int = 5

class TagRequest(BaseModel):
    item_id: str
    tag: str
