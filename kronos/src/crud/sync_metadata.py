import psycopg2.extras
from config.db import get_conn
from datetime import datetime


def get_last_sync_date(sync_type):
    """Get the last sync date for a specific sync type."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT last_sync_date FROM sync_metadata 
                WHERE sync_type = %s;
            """, (sync_type,))
            result = cur.fetchone()
            return result['last_sync_date'] if result else None


def update_sync_date(sync_type, sync_date=None, status='completed', error_message=None):
    """Update the sync date and status for a specific sync type."""
    if sync_date is None:
        sync_date = datetime.now()
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sync_metadata (sync_type, last_sync_date, sync_status, last_error, updated_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (sync_type) 
                DO UPDATE SET 
                    last_sync_date = EXCLUDED.last_sync_date,
                    sync_status = EXCLUDED.sync_status,
                    last_error = EXCLUDED.last_error,
                    updated_at = NOW();
            """, (sync_type, sync_date, status, error_message))
            conn.commit()


def set_sync_status(sync_type, status, error_message=None):
    """Set the sync status without updating the sync date."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE sync_metadata 
                SET sync_status = %s, last_error = %s, updated_at = NOW()
                WHERE sync_type = %s;
            """, (status, error_message, sync_type))
            conn.commit()


def get_all_sync_metadata():
    """Get all sync metadata records."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM sync_metadata 
                ORDER BY sync_type;
            """)
            return cur.fetchall()


def initialize_sync_metadata():
    """Initialize sync metadata with default values if not exists."""
    sync_types = ['planka_export', 'wiki_export']
    default_date = datetime(1900, 1, 1)
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            for sync_type in sync_types:
                cur.execute("""
                    INSERT INTO sync_metadata (sync_type, last_sync_date)
                    VALUES (%s, %s)
                    ON CONFLICT (sync_type) DO NOTHING;
                """, (sync_type, default_date))
            conn.commit()
