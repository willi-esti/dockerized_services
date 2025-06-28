import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / '.env')


def get_wiki_conn():
    """Get connection to Wiki.js database"""
    return psycopg2.connect(
        host=os.getenv('PG_SERVER_HOST'),
        port=os.getenv('PG_SERVER_PORT'),
        dbname='wiki',  # Wiki.js database name
        user=os.getenv('PG_SERVER_USER'),
        password=os.getenv('PG_SERVER_PASSWORD')
    )


def get_updated_pages(updated_after_date):
    """Get pages that have been updated after the specified date."""
    with get_wiki_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Convert datetime to string format that Wiki.js uses
            date_string = convert_datetime_to_wiki_format(updated_after_date)
            
            query = """
            SELECT 
                p.id,
                p.path,
                p.title,
                p.description,
                p.content,
                p."isPublished",
                p."isPrivate",
                p."updatedAt",
                p."createdAt",
                p."editorKey",
                p."localeCode",
                creator.name as creator_name,
                creator.email as creator_email,
                author.name as author_name,
                author.email as author_email
            FROM pages p
            LEFT JOIN users creator ON p."creatorId" = creator.id
            LEFT JOIN users author ON p."authorId" = author.id
            WHERE p."updatedAt" > %s
            ORDER BY p."updatedAt" DESC
            """
            
            cur.execute(query, (date_string,))
            return cur.fetchall()


def get_page_tags(page_id):
    """Get all tags for a specific page."""
    with get_wiki_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT t.tag, t.title
                FROM "pageTags" pt
                JOIN tags t ON pt."tagId" = t.id
                WHERE pt."pageId" = %s
                ORDER BY t.tag
            """, (page_id,))
            return cur.fetchall()


def get_page_links(page_id):
    """Get all links for a specific page."""
    with get_wiki_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT path, "localeCode"
                FROM "pageLinks"
                WHERE "pageId" = %s
                ORDER BY path
            """, (page_id,))
            return cur.fetchall()


def get_page_history(page_id, limit=10):
    """Get page history (recent versions)."""
    with get_wiki_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    ph.id,
                    ph.title,
                    ph.description,
                    ph."versionDate",
                    ph."editorKey",
                    ph.extra,
                    author.name as author_name,
                    author.email as author_email
                FROM "pageHistory" ph
                LEFT JOIN users author ON ph."authorId" = author.id
                WHERE ph.path = (SELECT path FROM pages WHERE id = %s LIMIT 1)
                    AND ph."localeCode" = (SELECT "localeCode" FROM pages WHERE id = %s LIMIT 1)
                ORDER BY ph."versionDate" DESC
                LIMIT %s
            """, (page_id, page_id, limit))
            return cur.fetchall()


def get_page_comments(page_id):
    """Get all comments for a specific page."""
    with get_wiki_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    c.id,
                    c.content,
                    c."createdAt",
                    c."updatedAt",
                    c."replyTo",
                    author.name as author_name,
                    author.email as author_email
                FROM comments c
                LEFT JOIN users author ON c."authorId" = author.id
                WHERE c."pageId" = %s
                ORDER BY c."createdAt"
            """, (page_id,))
            return cur.fetchall()


def get_page_complete_data(page_id):
    """Get complete data for a page including tags, links, history, and comments."""
    return {
        'tags': [dict(tag) for tag in get_page_tags(page_id)],
        'links': [dict(link) for link in get_page_links(page_id)],
        'history': [dict(history) for history in get_page_history(page_id)],
        'comments': [dict(comment) for comment in get_page_comments(page_id)]
    }


def convert_datetime_to_wiki_format(dt):
    """Convert Python datetime to Wiki.js string format."""
    # Wiki.js stores dates as ISO strings with milliseconds and Z suffix
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def parse_wiki_datetime(date_string):
    """Parse Wiki.js datetime string to Python datetime."""
    if not date_string:
        return None
    try:
        # Remove 'Z' suffix and parse
        if date_string.endswith('Z'):
            date_string = date_string[:-1]
        return datetime.fromisoformat(date_string)
    except (ValueError, TypeError):
        return date_string  # Return as-is if parsing fails
