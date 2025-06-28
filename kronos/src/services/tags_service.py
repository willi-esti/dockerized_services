from config import db
from crud.tags import get_tags, add_tag_to_knowledge_item

def get_all_tags():
    return get_tags()

def add_tag_to_item(item_id: str, tag: str):
    # Assuming item_id is a knowledge_item_id for now
    add_tag_to_knowledge_item(item_id, tag)
    return {"status": "success"}
