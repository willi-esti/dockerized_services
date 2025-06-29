#!/usr/bin/env python3

import requests
import json

def test_various_terms():
    """Test AI behavior with various single terms."""
    url = "http://localhost:8000/api/v1/chat/send"
    
    test_cases = [
        "backup",
        "presaje", 
        "doxero",
        "admin",
        "system",
        "unknown_term"
    ]
    
    for term in test_cases:
        print(f"\n=== Testing: '{term}' ===")
        
        payload = {
            "message": term,
            "conversation_id": None
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                action_taken = data.get('action_taken')
                iterations = data.get('iterations', 1)
                reply = data.get('reply', '')
                
                print(f"Action: {action_taken}")
                print(f"Iterations: {iterations}")
                print(f"Reply preview: {reply[:100]}...")
                
                if action_taken == 'respond' and iterations == 1:
                    if "search" in reply.lower():
                        print("✅ GOOD: AI searched and responded in 1 iteration")
                    else:
                        print("❌ BAD: AI responded without searching")
                elif action_taken == 'respond' and iterations > 1:
                    print("✅ GOOD: AI searched then responded")
                elif action_taken == 'max_iterations_reached':
                    print("⚠️ STUCK: AI got stuck in search loop")
                else:
                    print(f"⚠️ OTHER: {action_taken} in {iterations} iterations")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_various_terms()
