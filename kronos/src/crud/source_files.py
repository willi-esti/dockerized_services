import hashlib
import psycopg2.extras
from config.db import get_conn


def insert_source_file(knowledge_item_id, file_path, file_type, raw_text, sha256_hash):
    """Insert a new source file."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO source_files (knowledge_item_id, file_path, file_type, raw_text, sha256_hash)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (knowledge_item_id, file_path, file_type, raw_text, sha256_hash))
            return cur.fetchone()['id']


def file_exists_by_sha256(sha256_hash):
    """Check if a file exists by its SHA256 hash."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM source_files WHERE sha256_hash = %s LIMIT 1;", (sha256_hash,))
            return cur.fetchone() is not None


def sha256_of_text(text):
    """Generate SHA256 hash of text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def get_source_files_by_knowledge_item(knowledge_item_id):
    """Get all source files for a knowledge item."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM source_files 
                WHERE knowledge_item_id = %s
                ORDER BY created_at;
            """, (knowledge_item_id,))
            return cur.fetchall()


def delete_source_files_by_knowledge_item(knowledge_item_id):
    """Delete all source files for a knowledge item."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM source_files 
                WHERE knowledge_item_id = %s;
            """, (knowledge_item_id,))
            conn.commit()


def update_source_file(source_file_id, file_path=None, file_type=None, raw_text=None, sha256_hash=None):
    """Update an existing source file."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Build dynamic update query
            update_fields = []
            values = []
            
            if file_path is not None:
                update_fields.append("file_path = %s")
                values.append(file_path)
            if file_type is not None:
                update_fields.append("file_type = %s")
                values.append(file_type)
            if raw_text is not None:
                update_fields.append("raw_text = %s")
                values.append(raw_text)
            if sha256_hash is not None:
                update_fields.append("sha256_hash = %s")
                values.append(sha256_hash)
            
            # Always update the timestamp
            update_fields.append("updated_at = NOW()")
            values.append(source_file_id)
            
            if update_fields:
                query = f"""
                    UPDATE source_files 
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                    RETURNING id;
                """
                cur.execute(query, values)
                return cur.fetchone()['id']
            
            return source_file_id
