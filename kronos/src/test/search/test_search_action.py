#!/usr/bin/env python3

import requests
import json

def test_search_action():
    """Test if the search action format is working properly."""
    url = "http://localhost:8000/api/v1/chat/send"
    
    test_cases = [
        "backup",
        "doxero", 
        "ergo",
        "admin"
    ]
    
    for term in test_cases:
        print(f"\n=== Testing search for: '{term}' ===")
        
        payload = {
            "message": term,
            "conversation_id": None
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                action = data.get('action_taken', '')
                reasoning = data.get('reasoning', '')
                reply = data.get('reply', '')
                
                print(f"Action: {action}")
                print(f"Reasoning: {reasoning}")
                
                if "error" in reply.lower() and "no search query" in reply.lower():
                    print("❌ FAILED: Still getting 'no search query' error")
                elif action == 'respond' and "found" in reply.lower():
                    print("✅ SUCCESS: Searched and got results")
                elif action == 'respond' and "no results" in reply.lower():
                    print("✅ SUCCESS: Searched but no results found")
                else:
                    print(f"⚠️  UNCLEAR: {reply[:100]}...")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_search_action()
