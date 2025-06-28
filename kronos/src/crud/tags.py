import psycopg2.extras
from config.db import get_conn


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
