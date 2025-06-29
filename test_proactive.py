#!/usr/bin/env python3
"""
Test script to verify the AI now searches proactively and shares detailed results.
"""

import requests
import json

def test_proactive_search():
    """Test if AI searches database proactively and shares detailed results."""
    url = "http://localhost:8000/api/v1/chat/send"
    
    test_cases = [
        {
            "name": "Vague query that should trigger search",
            "message": "What's that thing about the elephant?"
        },
        {
            "name": "Specific query that should show detailed results",
            "message": "Show me what installation tasks you have"
        },
        {
            "name": "Unknown term that should search first",
            "message": "Tell me about Doxero"
        }
    ]
    
    headers = {"Content-Type": "application/json"}
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"Question: {test_case['message']}")
        print('='*60)
        
        try:
            payload = {"message": test_case['message']}
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                reply = result.get('reply', '')
                action_taken = result.get('action_taken', '')
                
                print(f"Action taken: {action_taken}")
                print(f"AI Response: {reply}")
                
                # Check if search was performed
                thinking_process = result.get('thinking_process', [])
                search_steps = [step for step in thinking_process if step.get('type') == 'database_search']
                
                if search_steps:
                    print(f"\n🔍 Search performed: YES ({len(search_steps)} searches)")
                    for j, step in enumerate(search_steps):
                        print(f"  Search {j+1}: '{step.get('search_query')}'")
                        print(f"  Results: {step.get('results_count', 0)}")
                        
                        # Check if results preview is shared
                        results_preview = step.get('results_preview', [])
                        if results_preview:
                            print(f"  Preview available: YES ({len(results_preview)} items)")
                            for k, preview in enumerate(results_preview[:2]):
                                title = preview.get('title', preview.get('content', '')[:50])
                                print(f"    {k+1}. {title}")
                        else:
                            print(f"  Preview available: NO")
                    
                    # Check if AI mentions specific file names or content in response
                    has_specifics = any(word in reply.lower() for word in ['card:', 'wiki:', '.md', '.sql', 'file:', 'task:', 'page:'])
                    print(f"📋 Mentions specific files/content: {'YES' if has_specifics else 'NO'}")
                else:
                    print(f"\n❌ Search performed: NO")
                    
                if action_taken == 'ask_clarification':
                    print(f"⚠️  AI asked for clarification instead of searching")
                
            else:
                print(f"Error: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_proactive_search()
