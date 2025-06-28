import os
import shutil
import tarfile
from datetime import datetime
from pathlib import Path


def create_archive_directory():
    """Create archive directory if it doesn't exist."""
    archive_path = os.getenv('ARCHIVE_PATH', '/app/archive')
    archive_dir = Path(archive_path)
    archive_dir.mkdir(parents=True, exist_ok=True)
    return archive_dir


def compress_and_archive_data(source_path, relative_path=""):
    """
    Compress data from source path and move to archive maintaining directory structure.
    
    Args:
        source_path (Path): Path to the source directory/file to compress
        relative_path (str): Relative path to maintain in archive structure
    
    Returns:
        Path: Path to the created archive file
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Source path does not exist: {source_path}")
    
    # Create archive directory
    archive_base = create_archive_directory()
    
    # Create timestamp for archive
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Determine archive structure
    if relative_path:
        # Maintain directory structure in archive
        archive_subdir = archive_base / relative_path
        archive_subdir.mkdir(parents=True, exist_ok=True)
        archive_name = f"{source_path.name}_{timestamp}.tar.gz"
        archive_path = archive_subdir / archive_name
    else:
        # Place directly in archive root
        archive_name = f"{source_path.name}_{timestamp}.tar.gz"
        archive_path = archive_base / archive_name
    
    # Create compressed archive
    with tarfile.open(archive_path, 'w:gz') as tar:
        if source_path.is_file():
            tar.add(source_path, arcname=source_path.name)
        else:
            # Add directory contents
            for item in source_path.iterdir():
                tar.add(item, arcname=item.name)
    
    return archive_path


def archive_imported_data(data_path):
    """
    Archive all imported data by compressing each top-level directory.
    
    Args:
        data_path (str): Path to the data directory
    
    Returns:
        list: List of created archive paths
    """
    data_dir = Path(data_path)
    if not data_dir.exists():
        return []
    
    archived_files = []
    
    # Process each top-level directory/file
    for item in data_dir.iterdir():
        try:
            if item.is_dir():
                # Archive directory (e.g., PRESAJe, wiki, PED)
                archive_path = compress_and_archive_data(item)
                archived_files.append(archive_path)
                
                # Remove original directory after successful archiving
                shutil.rmtree(item)
                
            elif item.is_file():
                # Archive individual file
                archive_path = compress_and_archive_data(item)
                archived_files.append(archive_path)
                
                # Remove original file after successful archiving
                item.unlink()
                
        except Exception as e:
            # Log error but continue with other items
            print(f"Error archiving {item}: {str(e)}")
            continue
    
    return archived_files


def archive_specific_folder(folder_path, folder_name):
    """
    Archive a specific folder maintaining its relative path structure.
    
    Args:
        folder_path (Path): Full path to the folder to archive
        folder_name (str): Name of the folder (used for relative path)
    
    Returns:
        Path: Path to the created archive file
    """
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder_path}")
    
    # Create archive with folder name as relative path
    archive_path = compress_and_archive_data(folder_path, folder_name)
    
    # Remove original folder after successful archiving
    shutil.rmtree(folder_path)
    
    return archive_path
