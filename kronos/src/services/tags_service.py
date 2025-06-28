from config import db

def get_all_tags():
    return db_config.get_tags()

def add_tag_to_item(item_id: str, tag: str):
    # Assuming item_id is a knowledge_item_id for now
    db_config.add_tag_to_knowledge_item(item_id, tag)
    return {"status": "success"}
