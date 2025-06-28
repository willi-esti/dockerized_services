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
