import numpy as np
import psycopg2
from psycopg2.extras import execute_values

DB_CONFIG = {
    'dbname': 'vector_brain',
    'user': 'postgres',
    'password': 'your-password',
    'host': 'localhost'
}

def search_similar_vectors(query_vector, top_k=5):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT k.title, c.chunk_text, c.vector <#> %s AS score
        FROM chunks c
        JOIN knowledge_items k ON c.knowledge_item_id = k.id
        ORDER BY score ASC
        LIMIT %s;
    """, (query_vector.tolist(), top_k))
    results = cur.fetchall()
    conn.close()
    return results
