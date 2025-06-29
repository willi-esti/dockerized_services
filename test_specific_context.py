#!/usr/bin/env python3
"""
Test script to verify the AI mentions admin systems context for Planka cards.
"""

import requests
import json

def test_planka_admin_context():
    """Test if AI mentions admin systems when discussing Planka cards."""
    url = "http://localhost:8000/api/v1/chat/send"
    
    payload = {
        "message": "Search for Planka cards and tell me what they are about. I want to understand what these tasks represent."
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        print("Testing Planka admin context...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            reply = result.get('reply', '')
            
            print(f"AI Response: {reply}")
            print("\n" + "="*50)
            
            # Check if AI mentions admin systems, administrative tasks, system management, etc.
            admin_keywords = [
                'admin systems', 'administrative', 'system administrators', 
                'admin', 'system management', 'created by admin', 'system maintenance'
            ]
            
            found_keywords = []
            for keyword in admin_keywords:
                if keyword.lower() in reply.lower():
                    found_keywords.append(keyword)
            
            if found_keywords:
                print(f"✅ AI mentioned admin context: {', '.join(found_keywords)}")
            else:
                print("❌ AI did not mention admin systems context")
                
            # Check thinking process for search results
            thinking_process = result.get('thinking_process', [])
            search_steps = [step for step in thinking_process if step.get('type') == 'database_search']
            
            if search_steps:
                print(f"\n🔍 Found {len(search_steps)} search steps")
                for step in search_steps:
                    print(f"Search query: {step.get('search_query')}")
                    results_count = step.get('results_count', 0)
                    print(f"Results found: {results_count}")
            
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_planka_admin_context()
