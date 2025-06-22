from services import memory_service

def process_chat(message: str, conversation_id: str = None):
    # 1. Search for relevant memory
    relevant_memory = memory_service.search_memory(message)

    # 2. Generate a reply (mocked for now)
    reply = f"Based on your question, I found the following information: {relevant_memory[0]['content'] if relevant_memory else 'No relevant information found.'}"

    # TODO: Store conversation history

    return {
        "reply": reply,
        "relevant_memory": relevant_memory
    }
