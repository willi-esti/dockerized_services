#!/usr/bin/env python3
"""
Test script to verify the complete file search integration in the chat API.
"""

import requests
import json
import sys

def test_chat_api():
    """Test the chat API endpoint with a simple query."""
    url = "http://localhost:8000/api/v1/chat/send"
    
    # Test with a query that should clearly identify data sources
    payload = {
        "message": "What are these cards? Are they from Planka? And what wiki documentation do you have?"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing chat API...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print("="*50)
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("="*50)
        
        if response.status_code == 200:
            result = response.json()
            print("Response:")
            print(json.dumps(result, indent=2))
            
            # Check if complete file search is working
            thinking_process = result.get('thinking_process', [])
            search_steps = [step for step in thinking_process if step.get('type') == 'database_search']
            
            if search_steps:
                print("\n" + "="*50)
                print("SEARCH ANALYSIS:")
                for step in search_steps:
                    print(f"- Search Query: {step.get('search_query')}")
                    print(f"- Search Method: {step.get('search_method')}")
                    print(f"- Result Type: {step.get('result_type')}")
                    print(f"- Results Count: {step.get('results_count')}")
                    
                    if step.get('results_preview'):
                        print("- Preview of results:")
                        for i, preview in enumerate(step['results_preview'][:2]):
                            if 'title' in preview:  # Complete file format
                                print(f"  {i+1}. {preview.get('title')} ({preview.get('file_type')})")
                                print(f"     Path: {preview.get('file_path')}")
                                print(f"     Content: {preview.get('content')[:100]}...")
                            else:  # Chunk format
                                print(f"  {i+1}. {preview.get('content')[:100]}...")
                    print()
            else:
                print("\nNo search steps found in thinking process")
                
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {response.text}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_chat_api()
