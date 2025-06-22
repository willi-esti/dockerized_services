from fastapi import APIRouter
from models_api.models import TagRequest
from services import tags_service

router = APIRouter()

@router.get("/tags")
def get_tags():
    return tags_service.get_all_tags()

@router.post("/tags")
def add_tag(request: TagRequest):
    return tags_service.add_tag_to_item(request.item_id, request.tag)
