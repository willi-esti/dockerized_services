from utils.logger import logger
from transformers import AutoTokenizer

def smart_overlap_chunk(
    file_path,
    cache_folder,
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    chunk_size_tok=256, 
    overlap_tok=50
):
    """
    Reads text from file_path, then applies token-based overlap chunking
    using the tokenizer's built-in striding mechanism.
    Returns a flat list of all overlapping token chunks as text.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_folder)
    
    # Determine the model's maximum sequence length, default to 512 if not specified
    model_max_len = tokenizer.model_max_length if hasattr(tokenizer, 'model_max_length') and tokenizer.model_max_length else 512

    # Validate chunk_size_tok against model_max_len.
    # The tokenizer will use chunk_size_tok as its max_length for creating chunks.
    if chunk_size_tok > model_max_len:
        logger(f"Warning: chunk_size_tok ({chunk_size_tok}) exceeds model_max_len ({model_max_len}). "
               f"Chunks will be effectively truncated to {model_max_len} by the model if not already by chunk_size_tok.", level="WARNING")
        # We proceed with chunk_size_tok, as SentenceTransformer will handle final truncation if needed.

    if overlap_tok >= chunk_size_tok:
        logger(f"Warning: overlap_tok ({overlap_tok}) is greater than or equal to chunk_size_tok ({chunk_size_tok}). "
               f"Adjusting overlap_tok to {chunk_size_tok // 3}.", level="WARNING")
        overlap_tok = chunk_size_tok // 3
        if overlap_tok < 0: # Ensure overlap is not negative if chunk_size_tok was 0 or 1
            overlap_tok = 0


    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    if not text.strip():
        logger(f"File {file_path} is empty or contains only whitespace. Skipping.", level="INFO")
        return []

    # Calculate stride: the number of tokens by which the window slides.
    # This is chunk_size minus the desired overlap.
    stride_val = chunk_size_tok - overlap_tok
    if stride_val <= 0: # Ensure positive stride to make progress
        stride_val = max(1, chunk_size_tok // 2 if chunk_size_tok > 0 else 1)
        logger(f"Adjusted stride_val to {stride_val} due to non-positive initial calculation.", level="DEBUG")


    # Tokenize the text, creating overlapping chunks.
    # `add_special_tokens=False` because we want clean text chunks.
    # The SentenceTransformer model will handle adding its own special tokens later.
    inputs = tokenizer(
        text,
        max_length=chunk_size_tok,       # Each chunk will be at most this many tokens
        truncation=True,                 # Truncate if text > max_length (for the first chunk)
        stride=stride_val,               # Number of tokens to slide the window
        return_overflowing_tokens=True, # Return all chunks, not just the first
        add_special_tokens=False,        # Do not add [CLS], [SEP] etc. here
        return_attention_mask=False,    # We only need input_ids for decoding
        return_token_type_ids=False   # We only need input_ids for decoding
    )

    all_text_chunks = []
    # `inputs['input_ids']` is a list of lists, where each inner list contains token IDs for a chunk.
    for chunk_token_ids in inputs['input_ids']:
        # Decode the token IDs back to a string
        chunk_text = tokenizer.decode(chunk_token_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        if chunk_text.strip(): # Ensure the chunk is not just whitespace
            all_text_chunks.append(chunk_text)
            #logger(f"File {file_path}, generated chunk: {len(chunk_token_ids)} tokens", level="DEBUG")

    # Fallback for very short texts that might not produce chunks with return_overflowing_tokens
    if not all_text_chunks and text.strip():
        logger(f"File {file_path} produced no chunks via striding (text might be shorter than chunk_size_tok). "
               "Treating entire content as a single chunk.", level="DEBUG")
        # Tokenize the whole text, truncating to chunk_size_tok if necessary
        single_chunk_ids = tokenizer.encode(text, max_length=chunk_size_tok, truncation=True, add_special_tokens=False)
        if single_chunk_ids:
            chunk_text = tokenizer.decode(single_chunk_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            if chunk_text.strip():
                all_text_chunks.append(chunk_text)
    
    # logger(f"File {file_path} successfully chunked into {len(all_text_chunks)} pieces.", level="INFO")
    return all_text_chunks