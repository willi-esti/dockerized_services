#!/usr/bin/env python3

import requests
import json

def test_simple_requests():
    """Test if the AI handles simple requests without asking for clarification."""
    url = "http://localhost:8000/api/v1/chat/send"
    
    test_cases = [
        "backup",
        "presaje",
        "doxero", 
        "help",
        "what can you do?",
        "show me something"
    ]
    
    for request in test_cases:
        print(f"\n=== Testing: '{request}' ===")
        
        payload = {
            "message": request,
            "conversation_id": None  # New conversation each time
        }
        
        try:
            response = requests.post(url, json=payload)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                action_taken = data.get('action_taken')
                reply = data.get('reply', '')
                
                print(f"Action: {action_taken}")
                print(f"Reply: {reply[:150]}...")
                
                if action_taken == 'ask_clarification':
                    print("❌ MIGHT BE TOO CAUTIOUS: AI asked for clarification")
                elif action_taken in ['respond', 'search_memory']:
                    print("✅ GOOD: AI took helpful action")
                else:
                    print(f"⚠️  Got action '{action_taken}'")
            else:
                print(f"❌ HTTP Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_requests()
