#!/usr/bin/env python3
"""
Script to reset sync dates to 1900 to force full re-sync.
"""

import sys
import os
sys.path.append('src')

from crud.sync_metadata import update_sync_date
from config.logger import logger
from datetime import datetime

def main():
    """Main function to reset sync dates."""
    logger("Resetting sync dates to 1900-01-01...", level='INFO')
    
    try:
        # Reset sync dates to 1900
        reset_date = datetime(1900, 1, 1)
        
        update_sync_date('planka_export', reset_date, 'completed')
        update_sync_date('wiki_export', reset_date, 'completed')
        
        logger("Successfully reset sync dates to 1900-01-01", level='INFO')
        logger("Next sync will export all data from the beginning", level='INFO')
        
        return 0
        
    except Exception as e:
        logger(f"Error: {str(e)}", level='ERROR')
        return 1

if __name__ == "__main__":
    exit(main())
