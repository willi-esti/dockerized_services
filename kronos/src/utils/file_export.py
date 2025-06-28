import os
from datetime import datetime
from pathlib import Path


def format_datetime(dt):
    """Format datetime object to string."""
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "Not set"


def create_export_directory(project_name):
    """Create directory for exporting card data."""
    data_path = os.getenv('DATA_PATH', '/app/data')
    project_dir = Path(data_path) / project_name.replace('/', '_').replace(' ', '_')
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def write_card_to_file(file_path, card_data):
    """Write card data to a text file in a readable format."""
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
