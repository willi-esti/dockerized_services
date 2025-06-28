#!/usr/bin/env python3
"""
Script to update existing chunks with proper embeddings.
Run this to fix any chunks that have zero embeddings.
"""

import sys
import os
sys.path.append('src')

from crud.import_data import update_existing_chunks_with_embeddings
from config.logger import logger

def main():
    """Main function to update embeddings."""
    logger("Starting embedding update process...", level='INFO')
    
    try:
        # Update existing chunks with proper embeddings
        stats = update_existing_chunks_with_embeddings()
        
        if 'error' in stats:
            logger(f"Error occurred: {stats['error']}", level='ERROR')
            return 1
        
        logger(f"Update completed successfully:", level='INFO')
        logger(f"  - Knowledge items processed: {stats['knowledge_items_processed']}", level='INFO')
        logger(f"  - Chunks updated: {stats['chunks_updated']}", level='INFO')
        logger(f"  - Errors: {stats['errors']}", level='INFO')
        
        return 0
        
    except Exception as e:
        logger(f"Unexpected error: {str(e)}", level='ERROR')
        return 1

if __name__ == "__main__":
    exit(main())
