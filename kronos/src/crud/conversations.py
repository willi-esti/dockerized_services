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

def get_all_conversations(limit: int = 50, offset: int = 0):
    """Get all conversations with basic info and message count."""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.id, 
                c.created_at, 
                c.updated_at,
                COUNT(cm.id) as message_count,
                MIN(CASE WHEN cm.sender = 'user' THEN cm.message END) as first_user_message
            FROM conversations c
            LEFT JOIN conversation_messages cm ON c.id = cm.conversation_id
            GROUP BY c.id, c.created_at, c.updated_at
            ORDER BY c.updated_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                "id": row[0],
                "created_at": row[1].isoformat() if row[1] else None,
                "updated_at": row[2].isoformat() if row[2] else None,
                "message_count": row[3] or 0,
                "first_user_message": row[4] or "New Conversation",
                "title": (row[4] or "New Conversation")[:50] + ("..." if row[4] and len(row[4]) > 50 else "")
            })
        
        cursor.close()
        conn.close()
        
        logger(f"Retrieved {len(conversations)} conversations", 'INFO')
        return conversations
        
    except Exception as e:
        logger(f"Error getting conversations: {str(e)}", 'ERROR')
        return []

def get_conversation_details(conversation_id: str):
    """Get full conversation details including all messages."""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        # Get conversation info
        cursor.execute("""
            SELECT id, created_at, updated_at
            FROM conversations
            WHERE id = %s
        """, (conversation_id,))
        
        conversation_row = cursor.fetchone()
        if not conversation_row:
            cursor.close()
            conn.close()
            return None
        
        # Get all messages
        messages = get_conversation_history(conversation_id, limit=1000)
        
        cursor.close()
        conn.close()
        
        return {
            "id": conversation_row[0],
            "created_at": conversation_row[1].isoformat() if conversation_row[1] else None,
            "updated_at": conversation_row[2].isoformat() if conversation_row[2] else None,
            "message_count": len(messages),
            "messages": messages,
            "title": messages[0]["message"][:50] + ("..." if len(messages[0]["message"]) > 50 else "") if messages else "Empty Conversation"
        }
        
    except Exception as e:
        logger(f"Error getting conversation details: {str(e)}", 'ERROR')
        return None
