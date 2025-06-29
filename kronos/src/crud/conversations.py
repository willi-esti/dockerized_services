from config.db import get_conn
from config.logger import logger
import json
import uuid
from datetime import datetime

def create_conversation():
    """Create a new conversation and return its ID."""
    conversation_id = str(uuid.uuid4())
    
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversations (id, created_at, updated_at)
            VALUES (%s, %s, %s)
        """, (conversation_id, datetime.now(), datetime.now()))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger(f"Created new conversation: {conversation_id}", 'INFO')
        return conversation_id
        
    except Exception as e:
        logger(f"Error creating conversation: {str(e)}", 'ERROR')
        return None

def add_message_to_conversation(conversation_id: str, message: str, sender: str, metadata: dict = None):
    """Add a message to a conversation."""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversation_messages (conversation_id, message, sender, metadata, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (conversation_id, message, sender, json.dumps(metadata or {}), datetime.now()))
        
        # Update conversation's updated_at
        cursor.execute("""
            UPDATE conversations SET updated_at = %s WHERE id = %s
        """, (datetime.now(), conversation_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger(f"Added {sender} message to conversation {conversation_id}", 'INFO')
        return True
        
    except Exception as e:
        logger(f"Error adding message to conversation: {str(e)}", 'ERROR')
        return False

def get_conversation_history(conversation_id: str, limit: int = 20):
    """Get conversation history with recent messages first."""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT message, sender, metadata, created_at
            FROM conversation_messages
            WHERE conversation_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (conversation_id, limit))
        
        messages = []
        for row in cursor.fetchall():
            metadata = row[2]
            if isinstance(metadata, str):
                metadata = json.loads(metadata) if metadata else {}
            elif metadata is None:
                metadata = {}
            # If metadata is already a dict, use it as-is
            
            messages.append({
                "message": row[0],
                "sender": row[1],
                "metadata": metadata,
                "timestamp": row[3].isoformat() if row[3] else None
            })
        
        cursor.close()
        conn.close()
        
        # Return in chronological order (oldest first)
        return list(reversed(messages))
        
    except Exception as e:
        logger(f"Error getting conversation history: {str(e)}", 'ERROR')
        return []

def build_conversation_context(conversation_id: str, max_context_length: int = 2000):
    """Build conversation context for AI from recent messages."""
    if not conversation_id:
        return ""
    
    history = get_conversation_history(conversation_id, limit=10)
    logger(f"Building context for conversation {conversation_id}, found {len(history)} messages", 'INFO')
    
    if not history:
        return ""
    
    # Exclude the very last message (current user message) since it will be passed separately
    if len(history) > 1:
        history = history[:-1]  # Remove the last message
    else:
        return ""  # If only one message, no context to build
    
    context_parts = ["Previous conversation:"]
    total_length = 0
    
    for msg in history:
        msg_text = f"\n{msg['sender'].upper()}: {msg['message']}"
        if total_length + len(msg_text) > max_context_length:
            break
        context_parts.append(msg_text)
        total_length += len(msg_text)
    
    if len(context_parts) == 1:  # Only the header, no actual messages
        return ""
    
    context_parts.append("\n\nBased on this conversation history, please respond to the latest message.")
    result = "".join(context_parts)
    logger(f"Built conversation context: {result[:200]}...", 'INFO')
    return result
