from services import memory_service
from services.ollama_service import ollama_service
from services.action_handler import action_handler
from config.logger import logger
from crud.conversations import create_conversation, add_message_to_conversation, build_conversation_context
from utils.token_counter import estimate_conversation_tokens, calculate_token_usage_percentage

def process_chat(message: str, conversation_id: str = None, max_iterations: int = 3):
    """Process chat with structured AI responses and action execution."""
    logger(f"Processing chat message: {message}", 'INFO')
    
    # Create new conversation if none provided
    if not conversation_id:
        conversation_id = create_conversation()
        logger(f"Created new conversation: {conversation_id}", 'INFO')
    
    # Add user message to conversation history
    add_message_to_conversation(conversation_id, message, "user")
    
    # Initialize conversation context
    context = {
        "conversation_id": conversation_id,
        "initial_query": message,
        "search_history": [],
        "iteration": 0
    }
    
    # Track thinking process for frontend display
    thinking_steps = []
    
    # Build initial context from conversation history
    conversation_context = build_conversation_context(conversation_id)
    initial_context = conversation_context
    
    iteration = 0
    token_usage = None
    token_info = None
    
    while iteration < max_iterations:
        iteration += 1
        logger(f"Chat iteration {iteration}/{max_iterations}", 'INFO')
        
        thinking_steps.append({
            "step": iteration,
            "type": "ai_thinking",
            "title": f"🧠 AI Analysis (Step {iteration})",
            "description": "Analyzing your question and deciding what action to take...",
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        
        # Get AI response with current context
        ai_response = ollama_service.generate_response(
            user_message=message,
            context=initial_context
        )
        
        # Calculate token usage for this request (only on first iteration)
        if iteration == 1:
            # Get system prompt from ollama service
            system_prompt = getattr(ollama_service, 'system_prompt', '')
            token_info = estimate_conversation_tokens(
                conversation_context=initial_context,
                user_message=message,
                system_prompt=system_prompt
            )
            
            # Determine model name from ollama service
            model_name = getattr(ollama_service, 'model_name', 'llama3')
            token_usage = calculate_token_usage_percentage(
                used_tokens=token_info["total_input_tokens"],
                model_name=model_name
            )
            
            logger(f"Token usage: {token_usage['used_tokens']}/{token_usage['max_tokens']} ({token_usage['usage_percentage']}%)", 'INFO')
        
        # Add AI decision to thinking steps
        thinking_steps.append({
            "step": iteration,
            "type": "ai_decision", 
            "title": f"💭 AI Decision",
            "description": f"Action: {ai_response.get('action', 'unknown')}",
            "reasoning": ai_response.get('reasoning', 'No reasoning provided'),
            "raw_response": ai_response,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        
        # Execute the action
        action_result = action_handler.execute_action(ai_response, context)
        
        # Handle different action results
        if action_result["type"] == "response":
            # AI provided a direct response, we're done
            thinking_steps.append({
                "step": iteration,
                "type": "final_response",
                "title": "✅ Final Response Ready",
                "description": "AI has enough information to provide a complete answer",
                "confidence": action_result.get("confidence", "medium"),
                "timestamp": __import__('datetime').datetime.now().isoformat()
            })
            
            # Save AI response to conversation history
            ai_metadata = {
                "confidence": action_result.get("confidence", "medium"),
                "sources": action_result.get("sources", []),
                "iterations": iteration,
                "action_taken": "respond"
            }
            add_message_to_conversation(conversation_id, action_result["message"], "ai", ai_metadata)
            
            return {
                "reply": action_result["message"],
                "relevant_memory": context.get("search_history", []),
                "confidence": action_result.get("confidence", "medium"),
                "sources": action_result.get("sources", []),
                "conversation_id": conversation_id,
                "iterations": iteration,
                "action_taken": "respond",
                "reasoning": ai_response.get("reasoning", ""),
                "thinking_process": thinking_steps,
                "token_usage": {
                    **token_usage,
                    "token_breakdown": token_info["breakdown"]
                }
            }
            
        elif action_result["type"] == "clarification":
            # AI needs clarification from user
            thinking_steps.append({
                "step": iteration,
                "type": "clarification_needed",
                "title": "❓ Need More Information",
                "description": "AI needs clarification to provide a better answer",
                "question": action_result["question"],
                "timestamp": __import__('datetime').datetime.now().isoformat()
            })
            
            # Save AI clarification question to conversation history
            ai_metadata = {
                "confidence": "high",
                "action_taken": "ask_clarification",
                "iterations": iteration
            }
            add_message_to_conversation(conversation_id, action_result["question"], "ai", ai_metadata)
            
            return {
                "reply": action_result["question"],
                "relevant_memory": context.get("search_history", []),
                "confidence": "high",
                "sources": [],
                "conversation_id": conversation_id,
                "iterations": iteration,
                "action_taken": "ask_clarification",
                "reasoning": ai_response.get("reasoning", ""),
                "thinking_process": thinking_steps,
                "token_usage": {
                    **token_usage,
                    "token_breakdown": token_info["breakdown"]
                }
            }
            
        elif action_result["type"] == "search_results":
            # AI searched memory, add results to context and continue
            results = action_result.get("results", [])
            
            thinking_steps.append({
                "step": iteration,
                "type": "database_search",
                "title": f"🔍 Database Search",
                "description": f"Searching for: '{action_result['query']}'",
                "search_query": action_result["query"],
                "search_type": action_result.get("search_type", "general"),
                "results_count": action_result["count"],
                "results_preview": [
                    {
                        "content": result.get('content', '')[:100] + "..." if len(result.get('content', '')) > 100 else result.get('content', ''),
                        "similarity": result.get('similarity', 'unknown')
                    }
                    for result in results[:3]
                ],
                "timestamp": __import__('datetime').datetime.now().isoformat()
            })
            
            context["search_history"].append({
                "query": action_result["query"],
                "results": results,
                "count": action_result["count"]
            })
            
            # Build context for next iteration
            if results:
                context_parts = []
                for result in results[:3]:  # Top 3 results
                    context_parts.append(f"- {result.get('content', '')[:200]}...")
                
                initial_context = f"""Previous search for "{action_result['query']}" found {action_result['count']} results:
{chr(10).join(context_parts)}

Based on this information, please provide a helpful response to the user's question: "{message}"
"""
                
                thinking_steps.append({
                    "step": iteration,
                    "type": "context_building",
                    "title": "📝 Building Context",
                    "description": f"Found {action_result['count']} relevant results, preparing context for next analysis",
                    "context_length": len(initial_context),
                    "timestamp": __import__('datetime').datetime.now().isoformat()
                })
            else:
                initial_context = f"""No results found for search: "{action_result['query']}"
Please provide a response indicating no relevant information was found for: "{message}"
"""
                
                thinking_steps.append({
                    "step": iteration,
                    "type": "no_results",
                    "title": "❌ No Results Found",
                    "description": f"No relevant information found for '{action_result['query']}'",
                    "timestamp": __import__('datetime').datetime.now().isoformat()
                })
            
            # Continue to next iteration with new context
            
        elif action_result["type"] == "multi_search_results":
            # Handle multiple search results
            search_results = action_result.get("searches", {})
            
            thinking_steps.append({
                "step": iteration,
                "type": "multi_search",
                "title": f"🔍 Multiple Database Searches",
                "description": f"Performing {len(search_results)} related searches",
                "searches": [
                    {
                        "query": query,
                        "type": data.get("type", "general"),
                        "results_count": data["count"],
                        "preview": [r.get('content', '')[:80] + "..." for r in data["results"][:2]]
                    }
                    for query, data in search_results.items()
                ],
                "timestamp": __import__('datetime').datetime.now().isoformat()
            })
            
            context["search_history"].extend([
                {"query": query, "results": data["results"], "count": data["count"]}
                for query, data in search_results.items()
            ])
            
            # Build comprehensive context
            context_parts = []
            for query, data in search_results.items():
                if data["results"]:
                    context_parts.append(f"\nSearch '{query}' found {data['count']} results:")
                    for result in data["results"][:2]:  # Top 2 per search
                        context_parts.append(f"- {result.get('content', '')[:150]}...")
                else:
                    context_parts.append(f"\nSearch '{query}' found no results.")
            
            initial_context = f"""Multiple searches performed:{''.join(context_parts)}

Based on this comprehensive information, please provide a helpful response to: "{message}"
"""
            
        elif action_result["type"] == "error":
            # Handle errors
            thinking_steps.append({
                "step": iteration,
                "type": "error",
                "title": "⚠️ Error Occurred",
                "description": f"Error: {action_result['message']}",
                "timestamp": __import__('datetime').datetime.now().isoformat()
            })
            
            logger(f"Action error: {action_result['message']}", 'ERROR')
            return {
                "reply": f"I encountered an error: {action_result['message']}",
                "relevant_memory": context.get("search_history", []),
                "confidence": "low",
                "sources": [],
                "conversation_id": conversation_id,
                "iterations": iteration,
                "action_taken": "error",
                "reasoning": ai_response.get("reasoning", ""),
                "thinking_process": thinking_steps,
                "token_usage": {
                    **token_usage,
                    "token_breakdown": token_info["breakdown"]
                } if token_usage else None
            }
    
    # If we've exceeded max iterations, return what we have
    thinking_steps.append({
        "step": iteration,
        "type": "max_iterations",
        "title": "⏱️ Maximum Iterations Reached",
        "description": f"Reached maximum of {max_iterations} iterations",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })
    
    logger(f"Max iterations ({max_iterations}) reached", 'WARNING')
    return {
        "reply": "I've searched through available information but need more time to provide a complete answer. Could you rephrase your question or be more specific?",
        "relevant_memory": context.get("search_history", []),
        "confidence": "low",
        "sources": [],
        "conversation_id": conversation_id,
        "iterations": iteration,
        "action_taken": "max_iterations_reached",
        "reasoning": "Maximum iterations reached",
        "thinking_process": thinking_steps,
        "token_usage": {
            **token_usage,
            "token_breakdown": token_info["breakdown"]
        } if token_usage else None
    }
