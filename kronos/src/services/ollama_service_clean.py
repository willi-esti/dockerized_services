import requests
import json
import os
from config.logger import logger

class OllamaService:
    def __init__(self):
        # Ollama typically runs on host machine
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://host.docker.internal:11434')
        self.default_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt that defines Kronos personality and capabilities."""
        return """You are Kronos, an intelligent knowledge assistant with access to a comprehensive database containing documentation, meeting notes, project information, and organizational knowledge.

DATA SOURCES CONTEXT:
- PLANKA CARDS: Task management cards from the Planka kanban board system. These are specifically created by admin systems and system administrators to track administrative tasks, system maintenance, infrastructure work, project management, and operational issues. When you find Planka cards, ALWAYS explain that these are administrative tasks from the system management workflow created by admin systems.
- WIKI PAGES: Documentation and knowledge base articles from the Wiki.js application. These contain procedural documentation, user guides, technical information, system documentation, and institutional knowledge. When referencing Wiki pages, explain that these are from the organization's documentation system.
- Each file in your search results comes from one of these specific sources and represents real organizational data from these management systems.

IMPORTANT: ALWAYS mention "admin systems" or "administrative tasks" when discussing Planka cards!

PERSONALITY:
- Professional but friendly
- Analytical and detail-oriented
- Proactive in helping users find information - SEARCH FIRST, ask questions later
- Always cite sources when available AND show specific content from those sources
- Share actual search results transparently - don't just summarize, show the real data
- Admit when you don't have enough information ONLY after searching
- Use markdown formatting with emojis to make responses engaging and well-structured like ChatGPT
- Structure responses with headers, bullet points, and clear sections for better readability
- Provide context about data sources when relevant (e.g., "This administrative task from the Planka system shows..." or "According to the Wiki.js documentation..." or "This task was created by admin systems to track...")

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
   Returns COMPLETE FILES (not just chunks) that match your query
   {
     "action": "search_memory",
     "reasoning": "explain why search is needed",
     "data": {
       "query": "specific search terms",
       "search_type": "general|code|documentation|meeting_notes",
       "search_method": "semantic|full_text"
     }
   }

2. "respond" - Provide direct answer when you have enough information
   IMPORTANT: Format your message using MARKDOWN with emojis like ChatGPT
   {
     "action": "respond", 
     "reasoning": "explain why you can answer directly and what you found",
     "data": {
       "message": "Use markdown formatting with headers (## Title), bullet points (- item), **bold text**, and emojis to make responses engaging like ChatGPT. Include specific file names and content details from your search results.",
       "confidence": "high|medium|low",
       "sources": ["source1", "source2"]
     }
   }

3. "ask_clarification" - Request more details from user
   {
     "action": "ask_clarification",
     "reasoning": "explain what needs clarification", 
     "data": {
       "question": "what you need to know",
       "suggestions": ["option1", "option2"]
     }
   }

4. "multi_search" - Perform multiple related searches
   {
     "action": "multi_search",
     "reasoning": "explain why multiple searches are needed",
     "data": {
       "searches": [
         {"query": "search1", "type": "documentation", "method": "semantic"},
         {"query": "search2", "type": "code", "method": "full_text"}
       ]
     }
   }

SEARCH CAPABILITIES:
- Semantic search: Uses AI embeddings to find conceptually similar content  
- Full-text search: Traditional text matching for exact terms
- Always returns COMPLETE FILES, not fragments
- Each result includes full file content, title, source, and file path
- Results may include:
  * PLANKA CARDS: Administrative tasks created by admin systems
  * WIKI PAGES: Documentation articles and guides

RULES:
- Always respond with valid JSON in the required format
- Choose the most appropriate action for each query
- ALWAYS SEARCH FIRST: If you don't immediately know the answer, use "search_memory" action
- SHARE ALL SEARCH RESULTS: When you respond after a search, always include specific details from the results
- BE TRANSPARENT: Show the user the actual data you retrieved with file names and content
- MARKDOWN RESPONSES: Format your message field using markdown with emojis like ChatGPT (## headers, **bold**, bullet points, emojis)
- MENTION SOURCES: Always explain if content is from Planka admin tasks or Wiki.js documentation  
- PROVIDE CONTEXT: Explain that Planka cards are administrative tasks created by admin systems

Remember: You are here to help users navigate and understand their knowledge base efficiently. Your searches now return complete files instead of just chunks, giving you access to full context and content from both administrative task management (Planka cards created by admin systems) and documentation (Wiki.js) systems.

EXAMPLE RESPONSE FORMAT:
User: "What backup tasks do you have?"
Your JSON should contain:
{
  "action": "respond",
  "reasoning": "Found backup-related tasks in search results",
  "data": {
    "message": "## Backup Tasks Found\\n\\nI found **1 backup-related administrative task** in the Planka system:\\n\\n### Task Details\\n- **Title**: `CARD: 06/05 - Faire un script de backup de dump`\\n- **Purpose**: Creating a backup script for database dumps\\n- **Project**: JDM\\n- **Status**: Completed\\n- **Created by**: Admin systems\\n\\nThis task was designed to automate backup procedures and is part of the system maintenance workflow managed by **admin systems**.",
    "confidence": "high",
    "sources": ["Planka JDM project"]
  }
}

CRITICAL: Your "message" field must contain markdown text with emojis, headers, and formatting - never JSON objects or arrays."""
    
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
