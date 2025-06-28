import os
import psycopg2
import psycopg2.extras
from pathlib import Path

from dotenv import load_dotenv
# Load .env from project root
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')

DB_PARAMS = {
    'host': os.getenv('PG_SERVER_HOST'),
    'port': os.getenv('PG_SERVER_PORT'),
    'dbname': os.getenv('PG_SERVER_NAME'),
    'user': os.getenv('PG_SERVER_USER'),
    'password': os.getenv('PG_SERVER_PASSWORD'),
}
print("Database parameters loaded:", DB_PARAMS)

def get_conn():
    """Get a database connection."""
    return psycopg2.connect(**DB_PARAMS)
