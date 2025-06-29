import requests
import json
import os
from config.logger import logger

class OllamaService:
    def __init__(self):
        # Ollama typically runs on host machine
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://host.docker.internal:11434')
        self.default_model = os.getenv('OLLAMA_MODEL', 'llama3')
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt that defines Kronos personality and capabilities."""
        return """You are Kronos, an intelligent knowledge assistant with access to a comprehensive database containing documentation, meeting notes, project information, and organizational knowledge.

PERSONALITY:
- Professional but friendly
- Analytical and detail-oriented  
- Proactive in helping users find information
- Always cite sources when available
- Admit when you don't have enough information

RESPONSE FORMAT:
You MUST respond with valid JSON in this exact format:

{
  "action": "ACTION_TYPE",
  "reasoning": "brief explanation of why you chose this action",
  "data": {
    // action-specific data
  }
}

ALLOWED ACTIONS:

1. "search_memory" - Search the knowledge database for more information
   {
     "action": "search_memory",
     "reasoning": "explain why search is needed",
     "data": {
       "query": "specific search terms",
       "search_type": "general|code|documentation|meeting_notes"
     }
   }

2. "respond" - Provide direct answer when you have enough information
   {
     "action": "respond", 
     "reasoning": "explain why you can answer directly",
     "data": {
       "message": "your response to the user",
       "confidence": "high|medium|low",
       "sources": ["source1", "source2"] // if applicable
     }
   }

3. "ask_clarification" - Request more details from user
   {
     "action": "ask_clarification",
     "reasoning": "explain what needs clarification", 
     "data": {
       "question": "what you need to know",
       "suggestions": ["option1", "option2"] // optional
     }
   }

4. "multi_search" - Perform multiple related searches
   {
     "action": "multi_search",
     "reasoning": "explain why multiple searches are needed",
     "data": {
       "searches": [
         {"query": "search1", "type": "documentation"},
         {"query": "search2", "type": "code"}
       ]
     }
   }

RULES:
- Always respond with valid JSON
- Choose the most appropriate action for each query
- If you have context from previous searches, use "respond" action
- If the query is vague, use "ask_clarification"
- If you need specific information not in context, use "search_memory"
- For complex topics, consider "multi_search"

Remember: You are here to help users navigate and understand their knowledge base efficiently."""
    
    def generate_response(self, user_message: str, context: str = "", model: str = None) -> dict:
        """Generate a structured JSON response using Ollama."""
        try:
            model = model or self.default_model
            
            # Build the full prompt with system instructions, context, and user message
            full_prompt = f"""{self.system_prompt}

CURRENT CONTEXT:
{context if context else "No previous context available."}

USER MESSAGE: {user_message}

Respond with JSON only:"""

            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "format": "json"  # Request JSON format from Ollama
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '{}')
                
                try:
                    # Parse the JSON response
                    parsed_response = json.loads(ai_response)
                    
                    # Validate the response has required fields
                    if not all(key in parsed_response for key in ['action', 'reasoning', 'data']):
                        raise ValueError("Missing required fields in AI response")
                    
                    return parsed_response
                    
                except (json.JSONDecodeError, ValueError) as e:
                    logger(f"Failed to parse AI JSON response: {e}", 'ERROR')
                    logger(f"Raw response: {ai_response}", 'DEBUG')
                    
                    # Return fallback response
                    return {
                        "action": "respond",
                        "reasoning": "AI response parsing failed, providing fallback",
                        "data": {
                            "message": ai_response if ai_response else "I couldn't process your request properly. Please try again.",
                            "confidence": "low"
                        }
                    }
                    
            else:
                logger(f"Ollama API error: {response.status_code} - {response.text}", 'ERROR')
                return {
                    "action": "respond",
                    "reasoning": "API error occurred",
                    "data": {
                        "message": "Sorry, I'm having trouble connecting to the AI service. Please try again.",
                        "confidence": "low"
                    }
                }
                
        except requests.exceptions.RequestException as e:
            logger(f"Error connecting to Ollama: {e}", 'ERROR')
            return {
                "action": "respond", 
                "reasoning": "Connection error",
                "data": {
                    "message": "Sorry, I'm having trouble connecting to the AI service. Please try again.",
                    "confidence": "low"
                }
            }
        except Exception as e:
            logger(f"Unexpected error in Ollama service: {e}", 'ERROR')
            return {
                "action": "respond",
                "reasoning": "Unexpected error",
                "data": {
                    "message": "Sorry, something went wrong. Please try again.",
                    "confidence": "low"
                }
            }
    
    def list_models(self) -> list:
        """List available Ollama models."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger(f"Error getting Ollama models: {e}", 'ERROR')
            return []
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

# Global instance
ollama_service = OllamaService()
