import os
import psycopg2
import psycopg2.extras
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / '.env')


def get_planka_conn():
    """Get connection to Planka database"""
    return psycopg2.connect(
        host=os.getenv('PG_SERVER_HOST'),
        port=os.getenv('PG_SERVER_PORT'),
        dbname='planka',  # Planka database name
        user=os.getenv('PG_SERVER_USER'),
        password=os.getenv('PG_SERVER_PASSWORD')
    )


def get_updated_cards(updated_after_date):
    """Get cards that have been updated after the specified date."""
    with get_planka_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            query = """
            SELECT 
                c.id,
                c.name as title,
                c.description,
                c.updated_at,
                c.created_at,
                c.due_date,
                p.id as project_id,
                p.name as project_name,
                b.name as board_name,
                l.name as list_name,
                creator.name as creator_name,
                creator.email as creator_email
            FROM card c
            JOIN list l ON c.list_id = l.id
            JOIN board b ON c.board_id = b.id
            JOIN project p ON b.project_id = p.id
            JOIN user_account creator ON c.creator_user_id = creator.id
            WHERE c.updated_at > %s
            ORDER BY p.name, c.updated_at DESC
            """
            
            cur.execute(query, (updated_after_date,))
            return cur.fetchall()


def get_card_tasks(card_id):
    """Get all tasks for a specific card."""
    with get_planka_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT name, is_completed, position, created_at, updated_at
                FROM task 
                WHERE card_id = %s 
                ORDER BY position
            """, (card_id,))
            return cur.fetchall()


def get_card_comments(card_id):
    """Get all comments for a specific card."""
    with get_planka_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    a.data,
                    a.created_at,
                    u.name as user_name,
                    u.email as user_email
                FROM action a
                JOIN user_account u ON a.user_id = u.id
                WHERE a.card_id = %s AND a.type = 'commentCard'
                ORDER BY a.created_at
            """, (card_id,))
            return cur.fetchall()


def get_card_members(card_id):
    """Get all members assigned to a specific card."""
    with get_planka_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    u.name,
                    u.email,
                    u.username,
                    cm.created_at as added_at
                FROM card_membership cm
                JOIN user_account u ON cm.user_id = u.id
                WHERE cm.card_id = %s
            """, (card_id,))
            return cur.fetchall()


def get_card_attachments(card_id):
    """Get all attachments for a specific card."""
    with get_planka_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    a.name as display_name,
                    a.filename,
                    a.dirname,
                    a.created_at,
                    creator.name as uploaded_by
                FROM attachment a
                JOIN user_account creator ON a.creator_user_id = creator.id
                WHERE a.card_id = %s
                ORDER BY a.created_at
            """, (card_id,))
            return cur.fetchall()


def get_card_complete_data(card_id):
    """Get complete data for a card including tasks, comments, members, and attachments."""
    return {
        'tasks': [dict(task) for task in get_card_tasks(card_id)],
        'comments': [dict(comment) for comment in get_card_comments(card_id)],
        'members': [dict(member) for member in get_card_members(card_id)],
        'attached_files': [dict(attachment) for attachment in get_card_attachments(card_id)]
    }
