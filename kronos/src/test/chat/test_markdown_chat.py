#!/usr/bin/env python3

import requests
import json
import time

def test_markdown_chat():
    """Test that the AI returns markdown-formatted responses"""
    
    base_url = "http://localhost:8000"
    
    # Send a message that should trigger markdown formatting
    # The backend will create a new conversation if conversation_id is None
    test_message = "Can you explain what this system does and show me some examples of the data sources?"
    
    print(f"💬 Sending message: {test_message}")
    print("🚀 Starting new conversation (automatic)...")
    
    chat_data = {
        "message": test_message,
        "conversation_id": None  # This will create a new conversation
    }
    
    chat_response = requests.post(f"{base_url}/api/v1/chat/send", json=chat_data)
    
    if chat_response.status_code != 200:
        print(f"❌ Chat request failed: {chat_response.status_code}")
        print(f"Response: {chat_response.text}")
        return
    
    response_data = chat_response.json()
    
    print("\n" + "="*80)
    print("RESPONSE ANALYSIS")
    print("="*80)
    
    # Check the AI response
    ai_message = response_data.get("response", "")
    print(f"\n📝 AI Response:\n{ai_message}")
    
    # Check for markdown elements
    markdown_indicators = [
        ("Headers", lambda text: "#" in text),
        ("Bold text", lambda text: "**" in text),
        ("Bullets", lambda text: "- " in text or "* " in text),
        ("Emojis", lambda text: any(ord(char) > 127 for char in text)),
        ("Code blocks", lambda text: "```" in text),
        ("Links", lambda text: "[" in text and "](" in text),
    ]
    
    print("\n🔍 Markdown Elements Found:")
    for name, check in markdown_indicators:
        found = check(ai_message)
        status = "✅" if found else "❌"
        print(f"  {status} {name}")
    
    # Check thinking process
    thinking_process = response_data.get("thinking_process", [])
    print(f"\n🧠 Thinking Steps: {len(thinking_process)}")
    for i, step in enumerate(thinking_process, 1):
        print(f"  {i}. {step.get('action', 'unknown')}: {step.get('description', 'no description')}")
    
    # Check token usage
    token_usage = response_data.get("token_usage", {})
    print(f"\n🔢 Token Usage:")
    print(f"  Prompt: {token_usage.get('prompt_tokens', 0)}")
    print(f"  Completion: {token_usage.get('completion_tokens', 0)}")
    print(f"  Total: {token_usage.get('total_tokens', 0)}")
    
    print("\n" + "="*80)
    
    # Check if it's actually markdown (not JSON or HTML)
    if ai_message.strip().startswith("{") or ai_message.strip().startswith("<"):
        print("⚠️  WARNING: Response looks like JSON or HTML, not markdown!")
    else:
        print("✅ Response appears to be markdown format!")

if __name__ == "__main__":
    test_markdown_chat()
