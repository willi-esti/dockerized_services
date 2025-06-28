from services import memory_service
from services.ollama_service import ollama_service

def process_chat(message: str, conversation_id: str = None):
    # 1. Search for relevant memory
    relevant_memory = memory_service.search_memory(message)
    
    # 2. Create context-aware prompt
    context = ""
    if relevant_memory:
        context = "\n".join([f"- {item['content'][:200]}..." for item in relevant_memory[:3]])
        
    prompt = f"""You are an AI assistant with access to a knowledge base. Use the following context to help answer the user's question.

Context from knowledge base:
{context if context else "No relevant context found."}

User question: {message}

Please provide a helpful response based on the context provided. If the context doesn't contain relevant information, let the user know and provide a general response."""

    # 3. Generate AI response
    ai_response = ollama_service.generate_response(prompt)

    # TODO: Store conversation history

    return {
        "reply": ai_response,
        "relevant_memory": relevant_memory,
        "conversation_id": conversation_id
    }
