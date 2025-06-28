import os
from datetime import datetime
from pathlib import Path


def format_datetime(dt):
    """Format datetime object to string."""
    if dt:
        if isinstance(dt, str):
            return dt
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "Not set"


def create_wiki_export_directory():
    """Create directory for exporting wiki page data."""
    data_path = os.getenv('DATA_PATH', '/app/data')
    wiki_dir = Path(data_path) / "wiki"
    wiki_dir.mkdir(parents=True, exist_ok=True)
    return wiki_dir


def sanitize_filename(filename):
    """Sanitize filename for filesystem."""
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def write_wiki_page_to_file(file_path, page_data):
    """Write wiki page data to a text file in a readable format."""
    content = []
    content.append("=" * 80)
    content.append(f"WIKI PAGE: {page_data.get('title', 'Untitled')}")
    content.append("=" * 80)
    content.append("")
    
    # Basic info
    content.append("BASIC INFORMATION:")
    content.append("-" * 20)
    content.append(f"ID: {page_data.get('id')}")
    content.append(f"Path: {page_data.get('path')}")
    content.append(f"Locale: {page_data.get('localeCode', 'en')}")
    content.append(f"Editor: {page_data.get('editorKey', 'unknown')}")
    content.append(f"Published: {'Yes' if page_data.get('isPublished') else 'No'}")
    content.append(f"Private: {'Yes' if page_data.get('isPrivate') else 'No'}")
    content.append(f"Created: {format_datetime(page_data.get('createdAt'))}")
    content.append(f"Updated: {format_datetime(page_data.get('updatedAt'))}")
    content.append(f"Creator: {page_data.get('creator_name')} ({page_data.get('creator_email')})")
    content.append(f"Last Author: {page_data.get('author_name')} ({page_data.get('author_email')})")
    content.append("")
    
    # Description
    if page_data.get('description'):
        content.append("DESCRIPTION:")
        content.append("-" * 12)
        content.append(page_data['description'])
        content.append("")
    
    # Tags
    tags = page_data.get('tags', [])
    if tags:
        content.append("TAGS:")
        content.append("-" * 5)
        for tag in tags:
            tag_title = tag.get('title', tag.get('tag', ''))
            if tag_title and tag_title != tag.get('tag', ''):
                content.append(f"• {tag['tag']} ({tag_title})")
            else:
                content.append(f"• {tag['tag']}")
        content.append("")
    
    # Links
    links = page_data.get('links', [])
    if links:
        content.append("LINKED PAGES:")
        content.append("-" * 13)
        for link in links:
            locale_info = f" [{link['localeCode']}]" if link.get('localeCode') != page_data.get('localeCode') else ""
            content.append(f"• {link['path']}{locale_info}")
        content.append("")
    
    # Recent history
    history = page_data.get('history', [])
    if history:
        content.append("RECENT HISTORY:")
        content.append("-" * 15)
        for i, version in enumerate(history[:5], 1):  # Show only last 5 versions
            content.append(f"{i}. Version from {format_datetime(version['versionDate'])}")
            content.append(f"   Author: {version.get('author_name', 'Unknown')}")
            content.append(f"   Editor: {version.get('editorKey', 'unknown')}")
            if version.get('title') != page_data.get('title'):
                content.append(f"   Title: {version['title']}")
            if version.get('description'):
                content.append(f"   Description: {version['description']}")
        content.append("")
    
    # Comments
    comments = page_data.get('comments', [])
    if comments:
        content.append("COMMENTS:")
        content.append("-" * 9)
        for i, comment in enumerate(comments, 1):
            content.append(f"{i}. {comment.get('author_name', 'Anonymous')} ({format_datetime(comment['createdAt'])}):")
            content.append(f"   {comment['content']}")
            if comment.get('updatedAt') and comment['updatedAt'] != comment['createdAt']:
                content.append(f"   (Updated: {format_datetime(comment['updatedAt'])})")
            if comment.get('replyTo', 0) > 0:
                content.append(f"   (Reply to comment #{comment['replyTo']})")
            content.append("")
    
    # Main content
    content.append("CONTENT:")
    content.append("-" * 8)
    if page_data.get('content'):
        content.append(page_data['content'])
    else:
        content.append("(No content)")
    content.append("")
    
    content.append("=" * 80)
    content.append(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("=" * 80)
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
