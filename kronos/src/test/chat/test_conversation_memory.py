#!/usr/bin/env python3

import requests
import json

def test_conversation_memory():
    """Test if the AI remembers information from conversation context."""
    url = "http://localhost:8000/api/v1/chat/send"
    
    # Start a new conversation and tell AI the name
    print("=== Step 1: Tell AI the name ===")
    payload1 = {
        "message": "thx it's working but my name is rolo",
        "conversation_id": None  # New conversation
    }
    
    response1 = requests.post(url, json=payload1)
    if response1.status_code == 200:
        data1 = response1.json()
        conversation_id = data1.get('conversation_id')
        print(f"Conversation ID: {conversation_id}")
        print(f"AI Response: {data1.get('reply', '')[:100]}...")
        
        # Now ask what the name is
        print("\n=== Step 2: Ask for the name ===")
        payload2 = {
            "message": "what is my name?",
            "conversation_id": conversation_id
        }
        
        response2 = requests.post(url, json=payload2)
        if response2.status_code == 200:
            data2 = response2.json()
            reply = data2.get('reply', '')
            action = data2.get('action_taken', '')
            
            print(f"Action: {action}")
            print(f"Reply: {reply}")
            
            if "rolo" in reply.lower() or "Rolo" in reply:
                print("✅ SUCCESS: AI remembered the name from conversation!")
            else:
                print("❌ FAILED: AI did not remember the name from conversation")
                print(f"Full response: {data2}")
        else:
            print(f"❌ Error in step 2: {response2.status_code}")
    else:
        print(f"❌ Error in step 1: {response1.status_code}")

if __name__ == "__main__":
    test_conversation_memory()
