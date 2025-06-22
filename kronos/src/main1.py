import os, torch
from dotenv import load_dotenv

# Load environment variables from .env file in the same directory
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from sentence_transformers import SentenceTransformer
from ingest.embedder import embed_chunks
from ingest.loader import load_files
from ingest.chunker import smart_overlap_chunk
from utils.check_env import check_env_vars
from utils.logger import logger
from utils.db_utils import insert_knowledge_item, insert_source_file, insert_chunk, sha256_of_text, file_exists_by_sha256

def check_gpu():
    """
    Check if GPU is available and return the device.
    """
    if torch.cuda.is_available():
        return torch.device('cuda')
    else:
        return torch.device('cpu')

def main():
    # Check required environment variables
    if not check_env_vars(['DATA_PATH', 'LOG_PATH']):
        return

    # Set Model Cache Folder
    model_cache_folder = os.getenv('MODEL_CACHE_FOLDER', '/app/models')

    # Check if GPU is available
    device = check_gpu()
    if device.type == 'cuda':
        logger(f"GPU is available: {torch.cuda.get_device_name(0)}", level='INFO')
    else:
        logger("No GPU available, using CPU.", level='WARNING')


    data_path = os.getenv('DATA_PATH', '/app/data')
    logger("⏳ Loading files from input directory...", level="INFO")
    files = load_files(data_path)  # Use DATA_PATH from .env

    logger("File loading completed.", level='INFO')
    logger("===== Starting smart overlapping chunking ======", level='DEBUG')

    if not files:
        logger("No files to chunk. Exiting smart overlapping chunking.", level='WARNING')
        return
    for file in files:
        logger(f"Processing file for overlap chunks: {file}", level='DEBUG')
        try:
            with open(file, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            sha256_hash = sha256_of_text(raw_text)
            if file_exists_by_sha256(sha256_hash):
                logger(f"File {file} with sha256 {sha256_hash} already exists in the database. Skipping.", level='WARNING')
                continue
            overlap_chunks = smart_overlap_chunk(file, model_cache_folder)
            logger(f"File {file} split into {len(overlap_chunks)} overlap chunks.", level='INFO')
            # Insert knowledge item and source file into DB
            title = os.path.basename(file)
            summary = None  # You can add summary extraction logic here
            knowledge_item_id = insert_knowledge_item(title, summary)
            file_type = os.path.splitext(file)[1][1:]  # e.g., 'pdf', 'md', etc.
            # Ensure file is a string (not Path)
            source_file_id = insert_source_file(knowledge_item_id, str(file), file_type, raw_text, sha256_hash)

            logger("===== Starting Embedding ======", level='DEBUG')
            model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='/app/models/all-MiniLM-L6-v2')
            for idx, chunk in enumerate(overlap_chunks):
                embedding = embed_chunks(model, chunk)
                # Convert embedding to list of Python floats
                embedding = [float(x) for x in embedding]
                content_hash = sha256_of_text(chunk)
                insert_chunk(knowledge_item_id, chunk, embedding, idx, content_hash=content_hash)
            logger("Embedding completed.", level='INFO')
        except Exception as e:
            logger(f"Error processing file {file} for overlap chunks: {e}", level='ERROR')

    # Get the summary or metadata of the files processed
    logger("Starting ollama to get summary of the files processed...", level='INFO')
    



if __name__ == "__main__":
    main()
