#!/usr/bin/env python3

import requests
import json

def test_ergo():
    """Test if the AI searches for 'ergo' instead of asking for clarification."""
    url = "http://localhost:8000/api/v1/chat/send"
    
    payload = {
        "message": "ergo",
        "conversation_id": None
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            action_taken = data.get('action_taken')
            reply = data.get('reply', '')
            iterations = data.get('iterations', 1)
            
            print(f"Action taken: {action_taken}")
            print(f"Iterations: {iterations}")
            print(f"Reply: {reply[:200]}...")
            
            if action_taken == 'search_memory':
                print("✅ CORRECT: AI searched for 'ergo'")
            elif action_taken == 'respond':
                if "search" in reply.lower() or "found" in reply.lower():
                    print("✅ GOOD: AI searched and then responded")
                else:
                    print("❌ WRONG: AI responded without searching")
                    print(f"Full reply: {reply}")
            elif action_taken == 'max_iterations_reached':
                print("⚠️ AI searched but got stuck in loop - this indicates a search issue")
            else:
                print(f"⚠️  Unexpected action: {action_taken}")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ergo()
