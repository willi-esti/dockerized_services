from fastapi import FastAPI
from routes import chat, memory, tags, conversations

app = FastAPI(
    title="Memory Assistant API",
    description="API for a ChatGPT-like assistant with tagging, memory, and vector search features.",
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
    return {"message": "Welcome to the Memory Assistant API"}
