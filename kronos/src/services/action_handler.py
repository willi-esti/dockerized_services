from services import memory_service
from config.logger import logger
import json

class ActionHandler:
    """Handles execution of AI-requested actions."""
    
    def __init__(self):
        pass
    
    def execute_action(self, action_data: dict, conversation_context: dict = None) -> dict:
        """Execute an action based on AI response."""
        action_type = action_data.get('action')
        reasoning = action_data.get('reasoning', '')
        data = action_data.get('data', {})
        
        logger(f"Executing action: {action_type} - {reasoning}", 'INFO')
        
        if action_type == "search_memory":
            return self._handle_search_memory(data, conversation_context)
        elif action_type == "respond":
            return self._handle_respond(data)
        elif action_type == "ask_clarification":
            return self._handle_ask_clarification(data)
        elif action_type == "multi_search":
            return self._handle_multi_search(data, conversation_context)
        else:
            logger(f"Unknown action type: {action_type}", 'WARNING')
            return {
                "type": "error",
                "message": f"Unknown action: {action_type}"
            }
    
    def _handle_search_memory(self, data: dict, context: dict = None) -> dict:
        """Handle memory search action."""
        query = data.get('query', '')
        search_type = data.get('search_type', 'general')
        
        if not query:
            return {
                "type": "error", 
                "message": "No search query provided"
            }
        
        logger(f"Searching memory for: {query} (type: {search_type})", 'INFO')
        
        # Perform the search
        results = memory_service.search_memory(query, top_k=5)
        
        return {
            "type": "search_results",
            "query": query,
            "search_type": search_type,
            "results": results,
            "count": len(results) if results else 0
        }
    
    def _handle_respond(self, data: dict) -> dict:
        """Handle direct response action."""
        message = data.get('message', '')
        confidence = data.get('confidence', 'medium')
        sources = data.get('sources', [])
        
        return {
            "type": "response",
            "message": message,
            "confidence": confidence,
            "sources": sources
        }
    
    def _handle_ask_clarification(self, data: dict) -> dict:
        """Handle clarification request action."""
        question = data.get('question', '')
        suggestions = data.get('suggestions', [])
        
        return {
            "type": "clarification",
            "question": question,
            "suggestions": suggestions
        }
    
    def _handle_multi_search(self, data: dict, context: dict = None) -> dict:
        """Handle multiple searches action."""
        searches = data.get('searches', [])
        
        if not searches:
            return {
                "type": "error",
                "message": "No searches provided"
            }
        
        all_results = {}
        
        for search in searches:
            query = search.get('query', '')
            search_type = search.get('type', 'general')
            
            if query:
                logger(f"Multi-search: {query} (type: {search_type})", 'INFO')
                results = memory_service.search_memory(query, top_k=3)
                all_results[query] = {
                    "type": search_type,
                    "results": results,
                    "count": len(results) if results else 0
                }
        
        return {
            "type": "multi_search_results",
            "searches": all_results,
            "total_searches": len(searches)
        }

# Global instance
action_handler = ActionHandler()
