from config.db import get_conn
from config.logger import logger
from crud.import_data import generate_embedding

def search_complete_files(query: str, top_k: int = 5, similarity_threshold: float = 0.3):
    """
    Search for relevant chunks and return complete files instead of just chunks.
    
    Process:
    1. Generate embedding for the query
    2. Find chunks that match the query
    3. Get the knowledge items that contain those chunks
    4. Return the complete file content from source_files
    """
    try:
        # Generate embedding for the query
        query_embedding = generate_embedding(query)
        query_embedding_str = str(query_embedding)
        
        conn = get_conn()
        cursor = conn.cursor()
        
        # Search for relevant chunks and get the complete file content
        query_sql = """
        WITH chunk_search AS (
            SELECT DISTINCT
                c.knowledge_item_id,
                c.content as chunk_content,
                1 - (c.embedding::vector <=> %s::vector) as similarity,
                ki.title,
                ki.summary,
                ki.source,
                sf.raw_text,
                sf.file_path,
                sf.file_type
            FROM chunks c
            JOIN knowledge_items ki ON c.knowledge_item_id = ki.id
            LEFT JOIN source_files sf ON ki.id = sf.knowledge_item_id
            WHERE c.embedding IS NOT NULL
            ORDER BY similarity DESC
            LIMIT %s
        )
        SELECT 
            knowledge_item_id,
            title,
            summary,
            source,
            raw_text,
            file_path,
            file_type,
            similarity,
            chunk_content
        FROM chunk_search
        WHERE similarity >= %s
        ORDER BY similarity DESC;
        """
        
        cursor.execute(query_sql, (query_embedding_str, top_k * 2, similarity_threshold))
        results = cursor.fetchall()
        
        if not results:
            logger(f"No files found for query: {query}", 'INFO')
            return []
        
        # Process results and group by knowledge item to avoid duplicates
        files_found = {}
        
        for row in results:
            knowledge_item_id = str(row[0])
            
            if knowledge_item_id not in files_found:
                files_found[knowledge_item_id] = {
                    'knowledge_item_id': knowledge_item_id,
                    'title': row[1] or 'Unknown Title',
                    'summary': row[2] or '',
                    'source': row[3] or 'Unknown Source',
                    'content': row[4] or '',  # This is the complete raw_text
                    'file_path': row[5] or '',
                    'file_type': row[6] or '',
                    'similarity': float(row[7]) if row[7] else 0.0,
                    'matching_chunks': []
                }
            
            # Add the matching chunk info
            if row[8]:  # chunk_content
                files_found[knowledge_item_id]['matching_chunks'].append({
                    'content': row[8][:200] + "..." if len(row[8]) > 200 else row[8],
                    'similarity': float(row[7]) if row[7] else 0.0
                })
        
        # Convert to list and limit results
        final_results = list(files_found.values())[:top_k]
        
        logger(f"Found {len(final_results)} complete files for query: {query}", 'INFO')
        
        cursor.close()
        conn.close()
        
        return final_results
        
    except Exception as e:
        logger(f"Error searching complete files: {str(e)}", 'ERROR')
        return []

def search_files_by_content_text(query: str, top_k: int = 5):
    """
    Alternative search that uses text similarity on full file content.
    This is useful when you want to search the complete files directly.
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        # Search directly in the raw_text of source_files
        query_sql = """
        SELECT 
            sf.knowledge_item_id,
            ki.title,
            ki.summary,
            ki.source,
            sf.raw_text,
            sf.file_path,
            sf.file_type,
            ts_rank(to_tsvector('english', sf.raw_text), plainto_tsquery('english', %s)) as rank
        FROM source_files sf
        JOIN knowledge_items ki ON sf.knowledge_item_id = ki.id
        WHERE to_tsvector('english', sf.raw_text) @@ plainto_tsquery('english', %s)
        ORDER BY rank DESC
        LIMIT %s;
        """
        
        cursor.execute(query_sql, (query, query, top_k))
        results = cursor.fetchall()
        
        files = []
        for row in results:
            files.append({
                'knowledge_item_id': str(row[0]),
                'title': row[1] or 'Unknown Title',
                'summary': row[2] or '',
                'source': row[3] or 'Unknown Source',
                'content': row[4] or '',  # Complete file content
                'file_path': row[5] or '',
                'file_type': row[6] or '',
                'similarity': float(row[7]) if row[7] else 0.0,
                'search_type': 'full_text'
            })
        
        logger(f"Found {len(files)} files using full-text search for: {query}", 'INFO')
        
        cursor.close()
        conn.close()
        
        return files
        
    except Exception as e:
        logger(f"Error in full-text search: {str(e)}", 'ERROR')
        return []
