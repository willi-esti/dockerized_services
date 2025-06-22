import os
import psycopg2
import psycopg2.extras
import hashlib
import numpy as np
from pathlib import Path

from dotenv import load_dotenv
# Load .env from project root
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / '.env')

DB_PARAMS = {
    'host': os.getenv('PG_SERVER_HOST'),
    'port': os.getenv('PG_SERVER_PORT'),
    'dbname': os.getenv('PG_SERVER_NAME'),
    'user': os.getenv('PG_SERVER_USER'),
    'password': os.getenv('PG_SERVER_PASSWORD'),
}

def get_conn():
    return psycopg2.connect(**DB_PARAMS)

def insert_knowledge_item(title, summary=None):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO knowledge_items (title, summary)
                VALUES (%s, %s)
                RETURNING id;
            """, (title, summary))
            return cur.fetchone()['id']

def insert_source_file(knowledge_item_id, file_path, file_type, raw_text, sha256_hash):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO source_files (knowledge_item_id, file_path, file_type, raw_text, sha256_hash)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (knowledge_item_id, file_path, file_type, raw_text, sha256_hash))
            return cur.fetchone()['id']

def insert_chunk(knowledge_item_id, content, embedding, chunk_index, group_id=None, content_hash=None, duplicate_of=None):
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

def sha256_of_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def file_exists_by_sha256(sha256_hash):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM source_files WHERE sha256_hash = %s LIMIT 1;", (sha256_hash,))
            return cur.fetchone() is not None

def get_knowledge_items():
    """Fetch all knowledge items."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM knowledge_items ORDER BY created_at DESC;")
            return cur.fetchall()

def delete_knowledge_item(knowledge_item_id):
    """Delete a knowledge item and cascade to related files and chunks."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM knowledge_items WHERE id = %s;", (knowledge_item_id,))
            conn.commit()

def get_tags():
    """Fetch all tags."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT name, description FROM tags ORDER BY name;")
            return cur.fetchall()

def add_tag_to_knowledge_item(knowledge_item_id, tag_name):
    """Add a tag to a knowledge item."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # First, get the tag_id from the tag name
            cur.execute("SELECT id FROM tags WHERE name = %s;", (tag_name,))
            tag_row = cur.fetchone()
            if not tag_row:
                # Optionally, create the tag if it doesn't exist
                cur.execute("INSERT INTO tags (name) VALUES (%s) RETURNING id;", (tag_name,))
                tag_id = cur.fetchone()['id']
            else:
                tag_id = tag_row['id']

            # Insert the mapping
            cur.execute("""
                INSERT INTO knowledge_item_tags (knowledge_item_id, tag_id)
                VALUES (%s, %s)
                ON CONFLICT (knowledge_item_id, tag_id) DO NOTHING;
            """, (knowledge_item_id, tag_id))
            conn.commit()

def search_chunks_by_embedding(embedding, top_k=5):
    """Search for chunks by embedding similarity."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT content, 1 - (embedding <=> %s) as similarity
                FROM chunks
                ORDER BY similarity DESC
                LIMIT %s;
            """, (list(embedding), top_k))
            return cur.fetchall()
