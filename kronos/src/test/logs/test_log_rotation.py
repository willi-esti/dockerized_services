#!/usr/bin/env python3

import requests
import json
import time

def test_log_rotation():
    """Test the log rotation functionality."""
    base_url = "http://localhost:8000/api/v1/logs"
    
    print("=== Log Rotation Test ===\n")
    
    # 1. Check initial log status
    print("1. Initial log status:")
    response = requests.get(f"{base_url}/status")
    if response.status_code == 200:
        status = response.json()
        print(f"   Current log size: {status['current_log']['size_mb']} MB")
        print(f"   Rotated logs: {len(status['rotated_logs'])}")
        print(f"   Total size: {status['total_size_mb']} MB")
    else:
        print(f"   Error: {response.status_code}")
    
    # 2. Check log settings
    print("\n2. Log settings:")
    response = requests.get(f"{base_url}/settings")
    if response.status_code == 200:
        settings = response.json()
        for key, value in settings.items():
            print(f"   {key}: {value}")
    else:
        print(f"   Error: {response.status_code}")
    
    # 3. Generate some log entries
    print("\n3. Generating log entries...")
    chat_url = "http://localhost:8000/api/v1/chat/send"
    test_messages = ["test 1", "test 2", "test 3", "backup"]
    
    for msg in test_messages:
        try:
            response = requests.post(chat_url, json={"message": msg, "conversation_id": None})
            print(f"   Sent: {msg} -> {response.status_code}")
        except Exception as e:
            print(f"   Error sending {msg}: {e}")
        time.sleep(0.5)
    
    # 4. Force rotation
    print("\n4. Forcing log rotation...")
    response = requests.post(f"{base_url}/rotate")
    if response.status_code == 200:
        result = response.json()
        print(f"   {result['message']}")
    else:
        print(f"   Error: {response.status_code}")
    
    # 5. Check final status
    print("\n5. Final log status:")
    response = requests.get(f"{base_url}/status")
    if response.status_code == 200:
        status = response.json()
        print(f"   Current log size: {status['current_log']['size_mb']} MB")
        print(f"   Rotated logs: {len(status['rotated_logs'])}")
        print(f"   Total size: {status['total_size_mb']} MB")
        
        print("\n   Rotated log files:")
        for log in status['rotated_logs']:
            print(f"     {log['file']} - {log['size_mb']} MB ({log['modified']})")
    else:
        print(f"   Error: {response.status_code}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_log_rotation()
