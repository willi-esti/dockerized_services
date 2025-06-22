from utils import db_utils

def get_all_conversations(tag: str = None, time: str = None):
    # TODO: Implement filtering by tag and time
    return db_utils.get_knowledge_items() # For now, we treat knowledge items as conversations

def get_conversation_by_id(id: str):
    # TODO: Implement this properly
    return {"id": id, "history": [], "memory": []}
