import os
import torch
from pathlib import Path
from sentence_transformers import SentenceTransformer

from config.logger import logger


def check_gpu():
    """Check if GPU is available and return the device."""
    if torch.cuda.is_available():
        return torch.device('cuda')
    else:
        return torch.device('cpu')


def get_model_cache_folder():
    """Get the model cache folder from environment."""
    return os.getenv('MODEL_CACHE_FOLDER', '/app/models')


def load_sentence_transformer_model(cache_folder):
    """Load the sentence transformer model."""
    return SentenceTransformer('all-MiniLM-L6-v2', cache_folder=os.path.join(cache_folder, 'all-MiniLM-L6-v2'))


def extract_tag_from_path(file_path):
    """Extract tag from file path based on parent directory."""
    path = Path(file_path)
    data_path = Path(os.getenv('DATA_PATH', '/app/data'))
    
    try:
        # Get relative path from data directory
        relative_path = path.relative_to(data_path)
        # Get the first directory as tag
        if len(relative_path.parts) > 1:
            return relative_path.parts[0]
        else:
            return "general"
    except ValueError:
        # File is not under data path
        return "external"


def get_exported_files(data_path):
    """Get all exported .txt files from the data directory."""
    data_dir = Path(data_path)
    if not data_dir.exists():
        logger(f"Data directory {data_path} does not exist", level='WARNING')
        return []
    
    # Find all .txt files recursively
    txt_files = list(data_dir.rglob("*.txt"))
    logger(f"Found {len(txt_files)} exported files to import", level='INFO')
    
    return [str(f) for f in txt_files]
