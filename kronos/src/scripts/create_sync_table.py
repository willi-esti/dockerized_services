#!/usr/bin/env python3
"""
Script to create the sync_metadata table if it doesn't exist.
"""

import sys
import os
sys.path.append('src')

from config.db import get_conn
from config.logger import logger

def create_sync_metadata_table():
    """Create the sync_metadata table and initialize it."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Create the sync_metadata table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS sync_metadata (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        sync_type TEXT UNIQUE NOT NULL,
                        last_sync_date TIMESTAMP NOT NULL,
                        sync_status TEXT DEFAULT 'completed',
                        last_error TEXT,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                # Insert initial sync dates
                cur.execute("""
                    INSERT INTO sync_metadata (sync_type, last_sync_date) VALUES
                    ('planka_export', '1900-01-01 00:00:00'),
                    ('wiki_export', '1900-01-01 00:00:00')
                    ON CONFLICT (sync_type) DO NOTHING;
                """)
                
                conn.commit()
                logger("Successfully created sync_metadata table and initialized data", level='INFO')
                
    except Exception as e:
        logger(f"Error creating sync_metadata table: {str(e)}", level='ERROR')
        raise

def main():
    """Main function."""
    logger("Creating sync_metadata table...", level='INFO')
    
    try:
        create_sync_metadata_table()
        logger("Database setup completed successfully", level='INFO')
        return 0
        
    except Exception as e:
        logger(f"Error: {str(e)}", level='ERROR')
        return 1

if __name__ == "__main__":
    exit(main())
