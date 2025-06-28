import psycopg2.extras
from config.db import get_conn


def insert_knowledge_item(title, summary=None, foreign_id=None, source=None):
    """Insert a new knowledge item."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO knowledge_items (title, summary, foreign_id, source)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (title, summary, foreign_id, source))
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


def get_knowledge_item_by_foreign_id_and_source(foreign_id, source):
    """Get knowledge item by foreign_id and source."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM knowledge_items 
                WHERE foreign_id = %s AND source = %s
                LIMIT 1;
            """, (foreign_id, source))
            return cur.fetchone()


def update_knowledge_item(knowledge_item_id, title=None, summary=None, foreign_id=None, source=None):
    """Update an existing knowledge item."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Build dynamic update query
            update_fields = []
            values = []
            
            if title is not None:
                update_fields.append("title = %s")
                values.append(title)
            if summary is not None:
                update_fields.append("summary = %s")
                values.append(summary)
            if foreign_id is not None:
                update_fields.append("foreign_id = %s")
                values.append(foreign_id)
            if source is not None:
                update_fields.append("source = %s")
                values.append(source)
            
            # Always update the timestamp
            update_fields.append("updated_at = NOW()")
            values.append(knowledge_item_id)
            
            if update_fields:
                query = f"""
                    UPDATE knowledge_items 
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                    RETURNING id;
                """
                cur.execute(query, values)
                return cur.fetchone()['id']
            
            return knowledge_item_id
