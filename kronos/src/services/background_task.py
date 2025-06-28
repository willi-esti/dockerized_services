from utils.logger import logger
import asyncio
import os
import psycopg2
import psycopg2.extras
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

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

async def sync_databases():
    await export_updated_cards(datetime.now() - timedelta(days=100))  # Example: export cards updated in the last day
    """
    while True:
        logger("Starting database synchronization task...")
        # Here you would query database A and write to database B
        await check_and_migrate_data()
        await asyncio.sleep(10)  # wait 30 seconds between checks
        """

async def export_updated_cards(updated_after_date):
    """
    Export cards that have been updated after the specified date.
    
    Args:
        updated_after_date (datetime): Only export cards updated after this date
    """
    logger(f"Exporting cards updated after {updated_after_date}")
    
    try:
        with get_planka_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Query for updated cards with all related data
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
                cards = cur.fetchall()
                
                logger(f"Found {len(cards)} updated cards")
                
                for card in cards:
                    await export_single_card(card)
                    
    except Exception as e:
        logger(f"Error exporting updated cards: {str(e)}")

async def export_single_card(card):
    """Export a single card with all its related data"""
    try:
        card_id = card['id']
        project_name = card['project_name']
        
        # Get additional card data
        card_data = await get_card_complete_data(card_id)
        card_data.update(dict(card))  # Merge with basic card info
        
        # Create directory structure
        data_path = os.getenv('DATA_PATH', '/app/data')
        project_dir = Path(data_path) / project_name.replace('/', '_').replace(' ', '_')
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename with card ID
        filename = f"card_{card_id}.txt"
        file_path = project_dir / filename
        
        # Write card data to file
        await write_card_to_file(file_path, card_data)
        
        logger(f"Exported card {card_id} to {file_path}")
        
    except Exception as e:
        logger(f"Error exporting card {card_id}: {str(e)}")

async def get_card_complete_data(card_id):
    """Get complete data for a card including tasks, comments, members, and attachments"""
    with get_planka_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Get tasks
            cur.execute("""
                SELECT name, is_completed, position, created_at, updated_at
                FROM task 
                WHERE card_id = %s 
                ORDER BY position
            """, (card_id,))
            tasks = cur.fetchall()
            
            # Get comments (actions with type 'commentCard')
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
            comments = cur.fetchall()
            
            # Get members
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
            members = cur.fetchall()
            
            # Get attached files
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
            attachments = cur.fetchall()
            
            return {
                'tasks': [dict(task) for task in tasks],
                'comments': [dict(comment) for comment in comments],
                'members': [dict(member) for member in members],
                'attached_files': [dict(attachment) for attachment in attachments]
            }

async def write_card_to_file(file_path, card_data):
    """Write card data to a text file in a readable format"""
    
    def format_datetime(dt):
        if dt:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return "Not set"
    
    content = []
    content.append("=" * 60)
    content.append(f"CARD: {card_data.get('title', 'Untitled')}")
    content.append("=" * 60)
    content.append("")
    
    # Basic info
    content.append("BASIC INFORMATION:")
    content.append("-" * 20)
    content.append(f"ID: {card_data.get('id')}")
    content.append(f"Project: {card_data.get('project_name')}")
    content.append(f"Board: {card_data.get('board_name')}")
    content.append(f"List: {card_data.get('list_name')}")
    content.append(f"Created: {format_datetime(card_data.get('created_at'))}")
    content.append(f"Updated: {format_datetime(card_data.get('updated_at'))}")
    content.append(f"Due Date: {format_datetime(card_data.get('due_date'))}")
    content.append(f"Creator: {card_data.get('creator_name')} ({card_data.get('creator_email')})")
    content.append("")
    
    # Description
    if card_data.get('description'):
        content.append("DESCRIPTION:")
        content.append("-" * 12)
        content.append(card_data['description'])
        content.append("")
    
    # Tasks
    tasks = card_data.get('tasks', [])
    if tasks:
        content.append("TASKS:")
        content.append("-" * 6)
        for i, task in enumerate(tasks, 1):
            status = "✓" if task['is_completed'] else "○"
            content.append(f"{i}. {status} {task['name']}")
            content.append(f"   Created: {format_datetime(task['created_at'])}")
            if task['updated_at'] != task['created_at']:
                content.append(f"   Updated: {format_datetime(task['updated_at'])}")
        content.append("")
    
    # Members
    members = card_data.get('members', [])
    if members:
        content.append("MEMBERS:")
        content.append("-" * 8)
        for member in members:
            content.append(f"• {member['name']} ({member['email']})")
            content.append(f"  Added: {format_datetime(member['added_at'])}")
        content.append("")
    
    # Comments
    comments = card_data.get('comments', [])
    if comments:
        content.append("COMMENTS:")
        content.append("-" * 9)
        for i, comment in enumerate(comments, 1):
            content.append(f"{i}. {comment['user_name']} ({format_datetime(comment['created_at'])}):")
            comment_text = comment['data'].get('text', '') if isinstance(comment['data'], dict) else str(comment['data'])
            content.append(f"   {comment_text}")
            content.append("")
    
    # Attached files
    attachments = card_data.get('attached_files', [])
    if attachments:
        content.append("ATTACHED FILES:")
        content.append("-" * 15)
        for attachment in attachments:
            content.append(f"• {attachment['display_name']}")
            content.append(f"  File: {attachment['filename']}")
            content.append(f"  Uploaded: {format_datetime(attachment['created_at'])}")
            content.append(f"  By: {attachment['uploaded_by']}")
            content.append("")
    
    content.append("=" * 60)
    content.append(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("=" * 60)
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))

async def check_and_migrate_data():
    # This function should contain the logic to check for new data in database A
    # and migrate it to database B if necessary.
    logger("Checking for new data to migrate...")
    # Example logic:
    # - Connect to database A
    # - Query for new or updated records
    # - Insert or update records in database B
    pass
