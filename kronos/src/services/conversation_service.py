from crud.conversations import get_all_conversations as crud_get_all_conversations, get_conversation_details
from config.logger import logger

def get_all_conversations(tag: str = None, time: str = None, limit: int = 50, offset: int = 0):
    """Get all conversations with optional filtering."""
    # TODO: Implement filtering by tag and time when needed
    logger(f"Getting conversations with limit={limit}, offset={offset}", 'INFO')
    return crud_get_all_conversations(limit=limit, offset=offset)

def get_conversation_by_id(id: str):
    """Get a specific conversation with all its messages."""
    logger(f"Getting conversation details for {id}", 'INFO')
    return get_conversation_details(id)
