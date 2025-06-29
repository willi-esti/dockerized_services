#!/usr/bin/env python3
"""
Script to test and display sync metadata.
"""

import sys
import os

# Add the src directory to the path (going up two levels from test/sync/)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from crud.sync_metadata import get_all_sync_metadata, initialize_sync_metadata
from config.logger import logger

def main():
    """Main function to test sync metadata."""
    logger("Testing sync metadata functionality...", level='INFO')
    
    try:
        # Initialize sync metadata
        initialize_sync_metadata()
        logger("Initialized sync metadata", level='INFO')
        
        # Get all sync metadata
        metadata = get_all_sync_metadata()
        
        logger("Current sync metadata:", level='INFO')
        for record in metadata:
            logger(f"  - {record['sync_type']}: last sync = {record['last_sync_date']}, status = {record['sync_status']}", level='INFO')
            if record['last_error']:
                logger(f"    Last error: {record['last_error']}", level='WARNING')
        
        return 0
        
    except Exception as e:
        logger(f"Error: {str(e)}", level='ERROR')
        return 1

if __name__ == "__main__":
    exit(main())
