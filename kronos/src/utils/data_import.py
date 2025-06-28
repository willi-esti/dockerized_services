import os
import torch
from pathlib import Path
from config.logger import logger
from .archiving import archive_specific_folder


def check_gpu():
    """Check if GPU is available and return the device."""
    if torch.cuda.is_available():
        return torch.device('cuda')
    else:
        return torch.device('cpu')


def check_env_vars(required_vars):
    """Check if required environment variables are set."""
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger(f"Missing required environment variables: {', '.join(missing_vars)}", level='ERROR')
        return False
    return True


def load_files(data_path):
    """Load all text files from the data directory organized by folders."""
    data_dir = Path(data_path)
    if not data_dir.exists():
        logger(f"Data directory does not exist: {data_path}", level='WARNING')
        return {}
    
    files_by_folder = {}
    
    # Iterate through top-level directories (tags)
    for folder in data_dir.iterdir():
        if folder.is_dir():
            folder_name = folder.name
            files_by_folder[folder_name] = []
            
            # Load all .txt files in this folder
            for file_path in folder.glob("**/*.txt"):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        files_by_folder[folder_name].append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'content': content,
                            'relative_path': str(file_path.relative_to(folder))
                        })
                        
                    except Exception as e:
                        logger(f"Error reading file {file_path}: {str(e)}", level='ERROR')
                        continue
            
            logger(f"Loaded {len(files_by_folder[folder_name])} files from {folder_name}", level='INFO')
    
    return files_by_folder


def extract_title_from_content(content, filename):
    """Extract title from content or use filename as fallback."""
    lines = content.strip().split('\n')
    
    # Look for title patterns in the first few lines
    for i, line in enumerate(lines[:10]):
        line = line.strip()
        if line:
            # Check for various title patterns
            if line.startswith('# '):
                return line[2:].strip()
            elif line.startswith('CARD: ') or line.startswith('WIKI PAGE: '):
                return line.split(': ', 1)[1].strip()
            elif line.startswith('=') and i + 1 < len(lines):
                # Look for title after separator line
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith('='):
                    return next_line
    
    # Fallback to filename without extension
    return Path(filename).stem.replace('_', ' ').title()


def extract_summary_from_content(content, max_length=200):
    """Extract a summary from content."""
    lines = content.strip().split('\n')
    
    # Skip header lines and find content
    content_started = False
    summary_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and headers
        if not line or line.startswith('=') or line.startswith('-'):
            continue
        
        # Skip metadata sections
        if line.upper() in ['BASIC INFORMATION:', 'DESCRIPTION:', 'CONTENT:', 'TAGS:', 'TASKS:', 'MEMBERS:', 'COMMENTS:']:
            if line.upper() == 'CONTENT:':
                content_started = True
            continue
        
        # Start collecting summary after content section or from description
        if content_started or 'DESCRIPTION:' in ''.join(lines[:20]):
            if len(line) > 10:  # Ignore very short lines
                summary_lines.append(line)
                
                # Stop when we have enough content
                if len(' '.join(summary_lines)) >= max_length:
                    break
    
    if summary_lines:
        summary = ' '.join(summary_lines)
        # Truncate to max_length
        if len(summary) > max_length:
            summary = summary[:max_length].rsplit(' ', 1)[0] + '...'
        return summary
    
    return "No summary available"


def process_imported_data_and_archive(data_path):
    """
    Process imported data and archive it after successful import.
    
    Args:
        data_path (str): Path to the data directory
    
    Returns:
        dict: Summary of import and archiving results
    """
    # Check required environment variables
    if not check_env_vars(['DATA_PATH', 'LOG_PATH', 'ARCHIVE_PATH']):
        return {'success': False, 'error': 'Missing required environment variables'}
    
    # Check GPU availability
    device = check_gpu()
    if device.type == 'cuda':
        logger(f"GPU is available: {torch.cuda.get_device_name(0)}", level='INFO')
    else:
        logger("No GPU available, using CPU.", level='WARNING')
    
    logger("⏳ Loading files from input directory...", level="INFO")
    files_by_folder = load_files(data_path)
    
    if not files_by_folder:
        logger("No files to import. Exiting.", level='WARNING')
        return {'success': False, 'error': 'No files found to import'}
    
    total_files = sum(len(files) for files in files_by_folder.values())
    logger(f"Found {total_files} files across {len(files_by_folder)} folders", level='INFO')
    
    results = {
        'success': True,
        'imported_folders': 0,
        'imported_files': 0,
        'updated_files': 0,
        'archived_folders': [],
        'errors': []
    }
    
    # Import data by folder (each folder becomes a tag)
    for folder_name, files in files_by_folder.items():
        try:
            logger(f"Processing folder: {folder_name} ({len(files)} files)", level='INFO')
            
            # Import files for this folder/tag
            import_stats = import_folder_data(folder_name, files)
            
            if import_stats['imported'] > 0 or import_stats['updated'] > 0:
                results['imported_folders'] += 1
                results['imported_files'] += import_stats['imported']
                results['updated_files'] += import_stats['updated']
                
                # Archive the folder after successful import
                folder_path = Path(data_path) / folder_name
                if folder_path.exists():
                    try:
                        archive_path = archive_specific_folder(folder_path, folder_name)
                        results['archived_folders'].append(str(archive_path))
                        logger(f"Archived folder {folder_name} to {archive_path}", level='INFO')
                    except Exception as archive_error:
                        error_msg = f"Failed to archive folder {folder_name}: {str(archive_error)}"
                        logger(error_msg, level='ERROR')
                        results['errors'].append(error_msg)
            
        except Exception as e:
            error_msg = f"Error processing folder {folder_name}: {str(e)}"
            logger(error_msg, level='ERROR')
            results['errors'].append(error_msg)
    
    logger(f"Import and archiving completed. Processed {results['imported_folders']} folders, {results['imported_files']} new files, {results['updated_files']} updated files", level='INFO')
    
    return results


def import_folder_data(folder_name, files):
    """
    Import files from a specific folder using the CRUD functions.
    
    Args:
        folder_name (str): Name of the folder (used as tag)
        files (list): List of file dictionaries
    
    Returns:
        dict: Import statistics including imported, updated, duplicates, etc.
    """
    from crud.import_data import import_files_with_tag
    
    # Import files with the folder name as tag
    results = import_files_with_tag(files, folder_name)
    
    return results


def extract_foreign_id_and_source(filename, tag_name):
    """
    Extract foreign ID and source from filename and tag.
    
    Args:
        filename (str): Name of the file (e.g., 'card_1520250197530117751.txt', 'home_123.txt')
        tag_name (str): Tag name (e.g., 'PRESAJe', 'wiki')
    
    Returns:
        tuple: (foreign_id, source)
    """
    # Remove file extension
    name_without_ext = Path(filename).stem
    
    # Determine source based on tag name and filename pattern
    if tag_name.lower() == 'wiki' or 'wiki' in tag_name.lower():
        source = 'wiki'
        # Extract page ID from wiki filename (e.g., 'home_123' -> '123')
        if '_' in name_without_ext:
            parts = name_without_ext.split('_')
            # Last part should be the page ID
            foreign_id = parts[-1]
        else:
            foreign_id = name_without_ext
    elif name_without_ext.startswith('card_'):
        source = 'planka'
        # Extract card ID from planka filename (e.g., 'card_1520250197530117751' -> '1520250197530117751')
        foreign_id = name_without_ext.replace('card_', '')
    else:
        # Default case - try to determine from tag name
        source = tag_name.lower()
        foreign_id = name_without_ext
    
    return foreign_id, source
