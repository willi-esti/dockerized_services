from fastapi import APIRouter, UploadFile, File
from models_api.models import MemoryRequest, MemorySearchRequest
from services import memory_service
from typing import List

router = APIRouter()

@router.post("/memory")
def add_memory(request: MemoryRequest):
    return memory_service.add_memory(request.text, request.tags)

@router.post("/memory/upload")
def upload_memory_file(file: UploadFile = File(...)):
    # TODO: process uploaded file
    content = file.file.read().decode("utf-8")
    return memory_service.add_memory(content, ["file"])

@router.post("/memory/search")
def search_memory(request: MemorySearchRequest):
    return memory_service.search_memory(request.query, request.top_k)
