import asyncio
import uvicorn
from fastapi import FastAPI
from routes import chat, memory, tags, conversations
from config.logger import logger
from services.background_task import sync_databases

app = FastAPI(
    title="Kronos",
    description="API for a the kronos app, search in tasks and documentation",
    version="0.1.0",
    host="0.0.0.0",
    port=8000,
)

app.include_router(chat.router)
app.include_router(memory.router)
app.include_router(tags.router)
app.include_router(conversations.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Kronos API!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/version")
def get_version():
    return {"version": "0.1.0"}

@app.on_event("startup")
async def start_background_task():
    asyncio.create_task(sync_databases())