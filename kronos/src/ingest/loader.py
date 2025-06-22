import os
import pathlib
from utils.logger import logger

SUPPORTED_EXTENSIONS = ['.txt', '.md', '.pdf', '.json', '.csv']

def load_files(input_dir):
    files = []
    for path in pathlib.Path(input_dir).rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            logger(f"Found file: {path}", level="INFO")
        else:
            logger(f"Skipping file: {path}", level="DEBUG")
        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(path)
    return files
