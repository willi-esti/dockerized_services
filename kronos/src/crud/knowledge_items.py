import psycopg2.extras
from config.db import get_conn


def insert_knowledge_item(title, summary=None):
    """Insert a new knowledge item."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO knowledge_items (title, summary)
                VALUES (%s, %s)
                RETURNING id;
            """, (title, summary))
            return cur.fetchone()['id']


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
