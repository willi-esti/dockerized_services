from config.logger import logger
import asyncio
import os
import torch
from datetime import datetime, timedelta
from pathlib import Path

from crud.planka import get_updated_cards, get_card_complete_data
from crud.wiki import get_updated_pages, get_page_complete_data
from crud.import_data import import_files_with_tag
from crud.source_files import insert_source_file, sha256_of_text, file_exists_by_sha256
from crud.chunks import insert_chunk
from utils.file_export import create_export_directory, write_card_to_file
from utils.wiki_export import create_wiki_export_directory, write_wiki_page_to_file, sanitize_filename
from utils.data_import import process_imported_data_and_archive, load_files as load_exported_files
from utils.import_utils import check_gpu, get_model_cache_folder, load_sentence_transformer_model, extract_tag_from_path, get_exported_files
from ingest.loader import load_files
from ingest.chunker import smart_overlap_chunk
from ingest.embedder import embed_chunks
from config.check_env import check_env_vars

async def sync_databases():
    """Main synchronization function."""
    await export_updated_cards(datetime.now() - timedelta(days=10))
    await export_updated_wiki_pages(datetime.now() - timedelta(days=10))
    await import_exported_data()
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
        cards = get_updated_cards(updated_after_date)
        logger(f"Found {len(cards)} updated cards")
        
        for card in cards:
            await export_single_card(card)
                    
    except Exception as e:
        logger(f"Error exporting updated cards: {str(e)}")

async def export_single_card(card):
    """Export a single card with all its related data."""
    try:
        card_id = card['id']
        project_name = card['project_name']
        
        # Create directory structure
        project_dir = create_export_directory(project_name)
        
        # Create filename with card ID
        filename = f"card_{card_id}.txt"
        file_path = project_dir / filename
        
        # Check if file already exists
        if file_path.exists():
            logger(f"Card {card_id} already exported, skipping")
            return
        
        # Get additional card data
        card_data = get_card_complete_data(card_id)
        card_data.update(dict(card))  # Merge with basic card info
        
        # Write card data to file
        write_card_to_file(file_path, card_data)
        
        logger(f"Exported card {card_id} to {file_path}")
        
    except Exception as e:
        logger(f"Error exporting card {card_id}: {str(e)}")

async def export_updated_wiki_pages(updated_after_date):
    """
    Export wiki pages that have been updated after the specified date.
    
    Args:
        updated_after_date (datetime): Only export pages updated after this date
    """
    logger(f"Exporting wiki pages updated after {updated_after_date}")
    
    try:
        pages = get_updated_pages(updated_after_date)
        logger(f"Found {len(pages)} updated wiki pages")
        
        for page in pages:
            await export_single_wiki_page(page)
                    
    except Exception as e:
        logger(f"Error exporting updated wiki pages: {str(e)}")

async def export_single_wiki_page(page):
    """Export a single wiki page with all its related data."""
    try:
        page_id = page['id']
        page_path = page['path']
        
        # Create directory structure
        wiki_dir = create_wiki_export_directory()
        
        # Create filename from page path with ID
        if page_path and page_path != '/':
            # Remove leading slash and replace path separators with underscores
            base_filename = sanitize_filename(page_path.lstrip('/').replace('/', '_'))
        else:
            base_filename = "home"
        
        filename = f"{base_filename}_{page_id}.txt"
        file_path = wiki_dir / filename
        
        # Check if file already exists
        if file_path.exists():
            logger(f"Wiki page {page_id} ({page_path}) already exported, skipping")
            return
        
        # Get additional page data
        page_data = get_page_complete_data(page_id)
        page_data.update(dict(page))  # Merge with basic page info
        
        # Write page data to file
        write_wiki_page_to_file(file_path, page_data)
        
        logger(f"Exported wiki page {page_id} ({page_path}) to {file_path}")
        
    except Exception as e:
        logger(f"Error exporting wiki page {page_id}: {str(e)}")

async def import_exported_data():
    """Import exported data files into the knowledge base and archive them."""
    logger("Starting import of exported data files...")
    
    try:
        data_path = os.getenv('DATA_PATH', '/app/data')
        
        # Use the new import and archiving function
        results = process_imported_data_and_archive(data_path)
        
        if results['success']:
            logger(f"Import completed: {results['imported_folders']} folders, {results['imported_files']} files imported", level='INFO')
            logger(f"Archived {len(results['archived_folders'])} folders", level='INFO')
            
            if results['errors']:
                logger(f"Import had {len(results['errors'])} errors:", level='WARNING')
                for error in results['errors']:
                    logger(f"  - {error}", level='WARNING')
        else:
            error_msg = results.get('error', 'Unknown error during import')
            logger(f"Import failed: {error_msg}", level='ERROR')
            
    except Exception as e:
        logger(f"Error during import and archiving process: {str(e)}", level='ERROR')

async def check_and_migrate_data():
    """Check for new data to migrate between databases."""
    # This function should contain the logic to check for new data in database A
    # and migrate it to database B if necessary.
    logger("Checking for new data to migrate...")
    # Example logic:
    # - Connect to database A
    # - Query for new or updated records
    # - Insert or update records in database B
    pass
