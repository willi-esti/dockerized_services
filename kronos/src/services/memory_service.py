from utils import db_utils
from ingest import chunker, embedder
from sentence_transformers import SentenceTransformer

# It's inefficient to load the model every time. In a real app, you'd load it once.
# For this example, we load it when the service is initialized.
MODEL_NAME = 'all-MiniLM-L6-v2'
MODEL = SentenceTransformer(MODEL_NAME)

def add_memory(text: str, tags: list = None):
    """Adds a new memory to the database."""
    # 1. Create a knowledge item
    knowledge_item_id = db_utils.insert_knowledge_item(title="New Memory")

    # 2. Chunk the text
    # Note: The chunker expects a file path, so we'll save the text to a temporary file.
    # In a real app, you might adapt the chunker to handle raw text directly.
    with open("/tmp/temp_memory.txt", "w") as f:
        f.write(text)
    
    chunks = chunker.smart_overlap_chunk("/tmp/temp_memory.txt", cache_folder="./models", model_name=MODEL_NAME)

    # 3. Embed the chunks
    embeddings = embedder.embed_chunks(MODEL, chunks)

    # 4. Insert chunks into the database
    for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
        db_utils.insert_chunk(knowledge_item_id, chunk_text, embedding, i)

    # 5. Add tags
    if tags:
        for tag in tags:
            db_utils.add_tag_to_knowledge_item(knowledge_item_id, tag)

    return {"status": "success", "message": "Memory added."}

def search_memory(query: str, top_k: int = 5):
    """Searches for memories based on a query."""
    # 1. Embed the query
    query_embedding = embedder.embed_chunks(MODEL, [query])[0]

    # 2. Search for similar chunks
    results = db_utils.search_chunks_by_embedding(query_embedding, top_k)
    return results
