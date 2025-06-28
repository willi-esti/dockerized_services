import numpy as np
import psycopg2.extras
from config.db import get_conn


def insert_chunk(knowledge_item_id, content, embedding, chunk_index, group_id=None, content_hash=None, duplicate_of=None):
    """Insert a new chunk."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO chunks (knowledge_item_id, content, embedding, chunk_index, group_id, content_hash, duplicate_of)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                knowledge_item_id, content, list(embedding), chunk_index, group_id, content_hash, duplicate_of
            ))
            return cur.fetchone()['id']


def search_chunks_by_embedding(embedding, top_k=5):
    """Search for chunks by embedding similarity."""
    # Ensure embedding is a list of native Python floats
    if isinstance(embedding, np.ndarray):
        embedding = embedding.astype(float).tolist()
    else:
        embedding = [float(x) for x in embedding]
    
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, knowledge_item_id, content, 1 - (embedding <=> %s::vector) as similarity
                FROM chunks
                ORDER BY similarity DESC
                LIMIT %s;
            """, (embedding, top_k))
            return cur.fetchall()


def delete_chunks_by_knowledge_item(knowledge_item_id):
    """Delete all chunks for a knowledge item."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM chunks 
                WHERE knowledge_item_id = %s;
            """, (knowledge_item_id,))
            conn.commit()


def get_chunks_by_knowledge_item(knowledge_item_id):
    """Get all chunks for a knowledge item."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM chunks 
                WHERE knowledge_item_id = %s
                ORDER BY chunk_index;
            """, (knowledge_item_id,))
            return cur.fetchall()
