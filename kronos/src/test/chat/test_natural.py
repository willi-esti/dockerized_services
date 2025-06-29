#!/usr/bin/env python3
"""
Test natural language responses with specific search results.
"""

import requests
import json

def test_natural_responses():
    """Test if AI provides natural language responses with specific details."""
    url = "http://localhost:8000/api/v1/chat/send"
    
    payload = {
        "message": "What backup related tasks do you have? Show me the specific details."
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            reply = result.get('reply', '')
            
            print("AI Response:")
            print("=" * 50)
            print(reply)
            print("=" * 50)
            
            # Check if response contains specific details
            has_file_names = any(word in reply.lower() for word in ['card:', 'task:', 'file:', 'wiki:', '.md'])
            has_specifics = any(word in reply.lower() for word in ['backup', 'script', 'dump'])
            is_natural = not (reply.startswith('{') or reply.startswith('['))
            
            print(f"✅ Contains file names/specifics: {'YES' if has_file_names else 'NO'}")
            print(f"✅ Contains backup details: {'YES' if has_specifics else 'NO'}")
            print(f"✅ Natural language format: {'YES' if is_natural else 'NO'}")
            
            # Check search was performed
            thinking_process = result.get('thinking_process', [])
            search_steps = [step for step in thinking_process if step.get('type') == 'database_search']
            print(f"🔍 Search performed: {'YES' if search_steps else 'NO'}")
            
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_natural_responses()
