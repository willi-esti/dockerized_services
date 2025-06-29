#!/usr/bin/env python3

import requests
import json

def test_direct_responses():
    """Test if the AI gives direct, concise answers for conversation-based questions."""
    url = "http://localhost:8000/api/v1/chat/send"
    
    # Start a new conversation
    print("=== Step 1: Tell AI the name ===")
    payload1 = {
        "message": "my name is rolo",
        "conversation_id": None
    }
    
    response1 = requests.post(url, json=payload1)
    if response1.status_code == 200:
        data1 = response1.json()
        conversation_id = data1.get('conversation_id')
        print(f"AI Response: {data1.get('reply', '')[:100]}...")
        
        # Test direct name question
        print("\n=== Step 2: Ask for name directly ===")
        payload2 = {
            "message": "what is my name?",
            "conversation_id": conversation_id
        }
        
        response2 = requests.post(url, json=payload2)
        if response2.status_code == 200:
            data2 = response2.json()
            reply = data2.get('reply', '')
            
            print(f"Reply: {reply}")
            
            # Check if response is direct and concise (under 100 characters is good)
            if "rolo" in reply.lower() and len(reply) < 150:
                print("✅ SUCCESS: Direct, concise answer!")
            elif "rolo" in reply.lower():
                print("⚠️  PARTIAL: Correct but verbose")
            else:
                print("❌ FAILED: Incorrect or no name")
                
        # Test conversation summary
        print("\n=== Step 3: Ask for conversation summary ===")
        payload3 = {
            "message": "tell me what we talked about",
            "conversation_id": conversation_id
        }
        
        response3 = requests.post(url, json=payload3)
        if response3.status_code == 200:
            data3 = response3.json()
            reply = data3.get('reply', '')
            
            print(f"Summary length: {len(reply)} characters")
            print(f"Summary preview: {reply[:200]}...")
            
            if "rolo" in reply.lower() and "conversation" in reply.lower():
                print("✅ SUCCESS: Good conversation summary!")
            else:
                print("❌ FAILED: Poor summary")

if __name__ == "__main__":
    test_direct_responses()
