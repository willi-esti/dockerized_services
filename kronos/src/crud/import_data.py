import hashlib
import os
from sentence_transformers import SentenceTransformer
from crud.knowledge_items import insert_knowledge_item, get_knowledge_item_by_foreign_id_and_source, update_knowledge_item
from crud.source_files import insert_source_file, sha256_of_text, file_exists_by_sha256, get_source_files_by_knowledge_item, delete_source_files_by_knowledge_item
from crud.chunks import insert_chunk, delete_chunks_by_knowledge_item
from crud.tags import add_tag_to_knowledge_item
from config.logger import logger


# Global model instance (loaded once)
_embedding_model = None


def get_embedding_model():
    """Get or load the embedding model."""
    global _embedding_model
    if _embedding_model is None:
        cache_folder = os.getenv('MODEL_CACHE_FOLDER', '/app/models')
        model_path = os.path.join(cache_folder, 'all-MiniLM-L6-v2')
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=model_path)
        logger(f"Loaded SentenceTransformer model to {model_path}", level='INFO')
    return _embedding_model


def generate_embedding(text):
    """Generate embedding for a text."""
    model = get_embedding_model()
    # Convert to numpy array and then to list for JSON serialization
    embedding = model.encode([text], convert_to_numpy=True)[0]
    return embedding.tolist()


def import_knowledge_item_with_tag(title, summary, content, file_path, tag_name, foreign_id=None, source=None):
    """
    Import a knowledge item with associated tag, source file, and content.
    If a knowledge item with the same foreign_id and source exists, update it.
    
    Args:
        title (str): Title of the knowledge item
        summary (str): Summary of the content
        content (str): Full content text
        file_path (str): Original file path
        tag_name (str): Tag to associate with this item
        foreign_id (str): Original ID from source system (card ID, page ID, etc.)
        source (str): Source system ('planka', 'wiki', etc.)
    
    Returns:
        dict: Import result with IDs and status
    """
    try:
        # Calculate file hash for deduplication
        content_hash = sha256_of_text(content)
        
        # Check if knowledge item already exists by foreign_id and source
        existing_item = None
        if foreign_id and source:
            existing_item = get_knowledge_item_by_foreign_id_and_source(foreign_id, source)
        
        if existing_item:
            # Update existing knowledge item
            knowledge_item_id = existing_item['id']
            logger(f"Found existing knowledge item {knowledge_item_id} for foreign_id: {foreign_id}, source: {source}", level='DEBUG')
            
            # Update the knowledge item
            update_knowledge_item(knowledge_item_id, title, summary, foreign_id, source)
            logger(f"Updated knowledge item {knowledge_item_id}: {title}", level='DEBUG')
            
            # Check if the content has changed by comparing SHA256
            existing_source_files = get_source_files_by_knowledge_item(knowledge_item_id)
            content_changed = True
            
            if existing_source_files:
                # Check if any existing source file has the same hash
                for existing_file in existing_source_files:
                    if existing_file['sha256_hash'] == content_hash:
                        content_changed = False
                        logger(f"Content unchanged for knowledge item {knowledge_item_id} (same SHA256)", level='DEBUG')
                        break
            
            if content_changed:
                # Delete old source files and chunks, create new ones
                delete_source_files_by_knowledge_item(knowledge_item_id)
                delete_chunks_by_knowledge_item(knowledge_item_id)
                
                # Create new source file
                file_type = 'text'
                source_file_id = insert_source_file(
                    knowledge_item_id=knowledge_item_id,
                    file_path=file_path,
                    file_type=file_type,
                    raw_text=content,
                    sha256_hash=content_hash
                )
                logger(f"Created new source file {source_file_id} for updated knowledge item {knowledge_item_id}", level='DEBUG')
                
                # Create new chunks
                chunk_ids = create_chunks_from_content(knowledge_item_id, content)
                
                return {
                    'success': True,
                    'updated': True,
                    'content_changed': True,
                    'knowledge_item_id': knowledge_item_id,
                    'source_file_id': source_file_id,
                    'chunk_ids': chunk_ids,
                    'message': f'Successfully updated: {title}'
                }
            else:
                # Content hasn't changed, just ensure tag is associated
                add_tag_to_knowledge_item(knowledge_item_id, tag_name)
                
                return {
                    'success': True,
                    'updated': True,
                    'content_changed': False,
                    'knowledge_item_id': knowledge_item_id,
                    'message': f'Knowledge item up to date: {title}'
                }
        else:
            # Check for duplicate content across all knowledge items
            if file_exists_by_sha256(content_hash):
                logger(f"File with same content already exists (SHA256 duplicate): {file_path}", level='INFO')
                return {
                    'success': True,
                    'duplicate': True,
                    'message': f'File with same content already imported: {file_path}'
                }
            
            # Create new knowledge item
            knowledge_item_id = insert_knowledge_item(title, summary, foreign_id, source)
            logger(f"Created knowledge item {knowledge_item_id}: {title} (foreign_id: {foreign_id}, source: {source})", level='DEBUG')
            
            # Insert source file
            file_type = 'text'
            source_file_id = insert_source_file(
                knowledge_item_id=knowledge_item_id,
                file_path=file_path,
                file_type=file_type,
                raw_text=content,
                sha256_hash=content_hash
            )
            logger(f"Created source file {source_file_id} for {file_path}", level='DEBUG')
            
            # Add tag to knowledge item
            add_tag_to_knowledge_item(knowledge_item_id, tag_name)
            logger(f"Added tag '{tag_name}' to knowledge item {knowledge_item_id}", level='DEBUG')
            
            # Create chunks from content
            chunk_ids = create_chunks_from_content(knowledge_item_id, content)
            
            return {
                'success': True,
                'duplicate': False,
                'updated': False,
                'knowledge_item_id': knowledge_item_id,
                'source_file_id': source_file_id,
                'chunk_ids': chunk_ids,
                'message': f'Successfully imported: {title}'
            }
        
    except Exception as e:
        error_msg = f"Error importing {file_path}: {str(e)}"
        logger(error_msg, level='ERROR')
        return {
            'success': False,
            'error': error_msg
        }
        logger(f"Created source file {source_file_id} for {file_path}", level='DEBUG')
        
        # Add tag to knowledge item
        add_tag_to_knowledge_item(knowledge_item_id, tag_name)
        logger(f"Added tag '{tag_name}' to knowledge item {knowledge_item_id}", level='DEBUG')
        
        # Create chunks from content (basic chunking for now)
        chunk_ids = create_chunks_from_content(knowledge_item_id, content)
        
        return {
            'success': True,
            'duplicate': False,
            'knowledge_item_id': knowledge_item_id,
            'source_file_id': source_file_id,
            'chunk_ids': chunk_ids,
            'message': f'Successfully imported: {title}'
        }
        
    except Exception as e:
        error_msg = f"Error importing {file_path}: {str(e)}"
        logger(error_msg, level='ERROR')
        return {
            'success': False,
            'error': error_msg
        }


def create_chunks_from_content(knowledge_item_id, content, chunk_size=1000, overlap=100):
    """
    Create chunks from content text with proper embeddings.
    
    Args:
        knowledge_item_id (int): ID of the knowledge item
        content (str): Content to chunk
        chunk_size (int): Maximum size of each chunk
        overlap (int): Number of characters to overlap between chunks
    
    Returns:
        list: List of created chunk IDs
    """
    chunk_ids = []
    
    # Simple text chunking (can be enhanced with smart chunking later)
    if len(content) <= chunk_size:
        # Content fits in one chunk
        try:
            # Generate real embedding for the content
            embedding = generate_embedding(content)
            
            chunk_id = insert_chunk(
                knowledge_item_id=knowledge_item_id,
                content=content,
                embedding=embedding,
                chunk_index=0
            )
            chunk_ids.append(chunk_id)
            logger(f"Created chunk with embedding (size: {len(embedding)}) for knowledge item {knowledge_item_id}", level='DEBUG')
        except Exception as e:
            logger(f"Error creating chunk for knowledge item {knowledge_item_id}: {str(e)}", level='ERROR')
    else:
        # Split into multiple chunks
        start = 0
        chunk_index = 0
        
        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk_content = content[start:end]
            
            try:
                # Generate real embedding for each chunk
                embedding = generate_embedding(chunk_content)
                
                chunk_id = insert_chunk(
                    knowledge_item_id=knowledge_item_id,
                    content=chunk_content,
                    embedding=embedding,
                    chunk_index=chunk_index
                )
                chunk_ids.append(chunk_id)
                chunk_index += 1
                
                # Move start position with overlap
                start = end - overlap if end < len(content) else end
                
            except Exception as e:
                logger(f"Error creating chunk {chunk_index} for knowledge item {knowledge_item_id}: {str(e)}", level='ERROR')
                break
    
    logger(f"Created {len(chunk_ids)} chunks with embeddings for knowledge item {knowledge_item_id}", level='DEBUG')
    return chunk_ids


def import_files_with_tag(files, tag_name):
    """
    Import multiple files with the same tag.
    
    Args:
        files (list): List of file dictionaries with 'name', 'content', 'path'
        tag_name (str): Tag name to associate with all files
    
    Returns:
        dict: Import statistics and results
    """
    results = {
        'total_files': len(files),
        'imported': 0,
        'updated': 0,
        'duplicates': 0,
        'errors': 0,
        'error_details': []
    }
    
    for file_info in files:
        try:
            # Extract title and summary from content
            from utils.data_import import extract_title_from_content, extract_summary_from_content, extract_foreign_id_and_source
            
            title = extract_title_from_content(file_info['content'], file_info['name'])
            summary = extract_summary_from_content(file_info['content'])
            foreign_id, source = extract_foreign_id_and_source(file_info['name'], tag_name)
            
            # Import the knowledge item
            import_result = import_knowledge_item_with_tag(
                title=title,
                summary=summary,
                content=file_info['content'],
                file_path=file_info['path'],
                tag_name=tag_name,
                foreign_id=foreign_id,
                source=source
            )
            
            if import_result['success']:
                if import_result.get('duplicate', False):
                    results['duplicates'] += 1
                elif import_result.get('updated', False):
                    results['updated'] += 1
                else:
                    results['imported'] += 1
            else:
                results['errors'] += 1
                results['error_details'].append(import_result.get('error', 'Unknown error'))
                
        except Exception as e:
            results['errors'] += 1
            error_msg = f"Error processing file {file_info.get('name', 'unknown')}: {str(e)}"
            results['error_details'].append(error_msg)
            logger(error_msg, level='ERROR')
    
    logger(f"Import completed for tag '{tag_name}': {results['imported']} new, {results['updated']} updated, {results['duplicates']} duplicates, {results['errors']} errors", level='INFO')
    
    return results


def update_existing_chunks_with_embeddings():
    """
    Update all existing chunks that have zero embeddings with proper embeddings.
    This is useful for fixing existing data that was imported with placeholder embeddings.
    
    Returns:
        dict: Update statistics
    """
    try:
        from crud.chunks import get_chunks_by_knowledge_item
        from crud.knowledge_items import get_knowledge_items
        
        logger("Starting to update existing chunks with proper embeddings...", level='INFO')
        
        # Get all knowledge items
        knowledge_items = get_knowledge_items()
        
        stats = {
            'knowledge_items_processed': 0,
            'chunks_updated': 0,
            'errors': 0
        }
        
        for ki in knowledge_items:
            try:
                stats['knowledge_items_processed'] += 1
                chunks = get_chunks_by_knowledge_item(ki['id'])
                
                for chunk in chunks:
                    # Check if chunk has zero embeddings
                    if chunk['embedding'] and all(x == 0.0 for x in chunk['embedding']):
                        # Generate new embedding
                        new_embedding = generate_embedding(chunk['content'])
                        
                        # Update the chunk in database
                        from crud.chunks import update_chunk_embedding
                        update_chunk_embedding(chunk['id'], new_embedding)
                        
                        stats['chunks_updated'] += 1
                        logger(f"Updated embedding for chunk {chunk['id']}", level='DEBUG')
                
            except Exception as e:
                stats['errors'] += 1
                logger(f"Error processing knowledge item {ki['id']}: {str(e)}", level='ERROR')
        
        logger(f"Embedding update completed: {stats['chunks_updated']} chunks updated across {stats['knowledge_items_processed']} knowledge items", level='INFO')
        return stats
        
    except Exception as e:
        error_msg = f"Error updating embeddings: {str(e)}"
        logger(error_msg, level='ERROR')
        return {'error': error_msg}
