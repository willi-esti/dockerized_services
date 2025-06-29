"""
Token counting utilities for tracking AI context usage.
"""

def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.
    This is a rough approximation - actual tokenization may vary by model.
    
    General rules:
    - 1 token ≈ 4 characters for English text
    - 1 token ≈ 3/4 of a word on average
    - Punctuation and special characters may count as separate tokens
    """
    if not text:
        return 0
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Rough estimation: 1 token per 4 characters
    char_based_estimate = len(text) / 4
    
    # Word-based estimation: 1.3 tokens per word (accounting for punctuation)
    words = text.split()
    word_based_estimate = len(words) * 1.3
    
    # Use the higher estimate to be conservative
    return int(max(char_based_estimate, word_based_estimate))

def estimate_conversation_tokens(conversation_context: str, user_message: str, system_prompt: str = "") -> dict:
    """
    Estimate total tokens for a conversation request.
    
    Returns:
        dict with token breakdown and total
    """
    system_tokens = estimate_tokens(system_prompt)
    context_tokens = estimate_tokens(conversation_context)
    message_tokens = estimate_tokens(user_message)
    
    # Add some overhead for formatting and special tokens
    overhead = 50
    
    total_tokens = system_tokens + context_tokens + message_tokens + overhead
    
    return {
        "system_prompt_tokens": system_tokens,
        "conversation_context_tokens": context_tokens,
        "user_message_tokens": message_tokens,
        "overhead_tokens": overhead,
        "total_input_tokens": total_tokens,
        "breakdown": {
            "system": system_tokens,
            "context": context_tokens, 
            "message": message_tokens,
            "overhead": overhead
        }
    }

def get_model_limits() -> dict:
    """
    Get token limits for different models.
    These are approximate context windows.
    """
    return {
        "llama3": {
            "max_context_tokens": 8192,
            "recommended_max": 7000,  # Leave room for response
            "name": "Llama 3"
        },
        "llama3.1": {
            "max_context_tokens": 131072,  # 128k context
            "recommended_max": 120000,
            "name": "Llama 3.1"
        },
        "llama3.2": {
            "max_context_tokens": 131072,
            "recommended_max": 120000,
            "name": "Llama 3.2"
        },
        "default": {
            "max_context_tokens": 8192,
            "recommended_max": 7000,
            "name": "Default Model"
        }
    }

def calculate_token_usage_percentage(used_tokens: int, model_name: str = "default") -> dict:
    """
    Calculate what percentage of the model's context window is being used.
    """
    limits = get_model_limits()
    
    # Try to find the specific model, fall back to default
    model_key = model_name.lower().replace(":", "").replace("-", "")
    if model_key not in limits:
        # Try partial matching
        for key in limits.keys():
            if key in model_key or model_key in key:
                model_key = key
                break
        else:
            model_key = "default"
    
    model_limits = limits[model_key]
    max_tokens = model_limits["max_context_tokens"]
    recommended_max = model_limits["recommended_max"]
    
    usage_percentage = (used_tokens / max_tokens) * 100
    recommended_percentage = (used_tokens / recommended_max) * 100
    
    # Determine status
    if usage_percentage > 95:
        status = "critical"
    elif recommended_percentage > 90:
        status = "high"
    elif recommended_percentage > 70:
        status = "medium"
    else:
        status = "low"
    
    return {
        "used_tokens": used_tokens,
        "max_tokens": max_tokens,
        "recommended_max": recommended_max,
        "usage_percentage": round(usage_percentage, 1),
        "recommended_percentage": round(recommended_percentage, 1),
        "remaining_tokens": max_tokens - used_tokens,
        "status": status,
        "model_name": model_limits["name"]
    }
