#!/usr/bin/env python3

import requests
import json

def test_greeting():
    """Test if the AI responds naturally to simple greetings."""
    url = "http://localhost:8000/api/v1/chat/send"
    
    test_cases = [
        "hi",
        "hello", 
        "hey there",
        "good morning"
    ]
    
    for greeting in test_cases:
        print(f"\n=== Testing: '{greeting}' ===")
        
        payload = {
            "message": greeting,
            "conversation_id": None  # New conversation each time
        }
        
        try:
            response = requests.post(url, json=payload)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check the new response format
                action_taken = data.get('action_taken')
                reply = data.get('reply', '')
                
                print(f"Action: {action_taken}")
                print(f"Reply: {reply[:100]}...")
                
                if action_taken == 'ask_clarification':
                    print("❌ FAILED: AI asked for clarification on simple greeting")
                elif action_taken == 'respond':
                    if any(greeting in reply for greeting in ["Hello", "Hi", "Good morning", "👋", "🤗", "🌞"]):
                        print("✅ PASSED: AI responded naturally with a greeting")
                    else:
                        print("⚠️  AI responded but without a proper greeting")
                else:
                    print(f"⚠️  UNEXPECTED: Got action '{action_taken}'")
            else:
                print(f"❌ HTTP Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_greeting()
