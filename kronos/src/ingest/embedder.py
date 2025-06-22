from utils.logger import logger
import os

def embed_chunks(model, chunks):
    return model.encode(chunks, show_progress_bar=False, convert_to_numpy=True)

#print("Embedding model loaded successfully.")
#t = embed_chunks(["This is a test chunk.", "Here is another chunk for embedding."])  # Example usage

#print("Embedding completed.")
