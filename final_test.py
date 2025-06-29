#!/usr/bin/env python3
"""
Final test to confirm the AI properly explains both Planka admin tasks and Wiki.js documentation.
"""

import requests
import json

def final_test():
    """Test the AI's understanding of admin systems and documentation."""
    url = "http://localhost:8000/api/v1/chat/send"
    
    # Test 1: Ask about both types of data
    payload1 = {
        "message": "Can you explain what data sources you have access to and what they represent?"
    }
    
    # Test 2: Ask for specific search
    payload2 = {
        "message": "Search for any admin tasks related to installation or setup"
    }
    
    for i, payload in enumerate([payload1, payload2], 1):
        print(f"\n{'='*50}")
        print(f"TEST {i}: {payload['message']}")
        print('='*50)
        
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                reply = result.get('reply', '')
                
                print(f"AI Response: {reply}")
                
                # Check for key terms
                admin_terms = ['admin systems', 'administrative', 'system management', 'created by admin']
                wiki_terms = ['wiki.js', 'documentation', 'guides', 'knowledge base']
                
                found_admin = any(term.lower() in reply.lower() for term in admin_terms)
                found_wiki = any(term.lower() in reply.lower() for term in wiki_terms)
                
                print(f"\n✅ Mentions admin context: {'Yes' if found_admin else 'No'}")
                print(f"✅ Mentions Wiki.js context: {'Yes' if found_wiki else 'No'}")
                
                # Check if search was performed
                thinking_process = result.get('thinking_process', [])
                search_steps = [step for step in thinking_process if step.get('type') == 'database_search']
                
                if search_steps:
                    print(f"🔍 Performed {len(search_steps)} searches")
                    for step in search_steps:
                        print(f"  - Query: {step.get('search_query')}")
                        print(f"  - Results: {step.get('results_count')}")
                
            else:
                print(f"Error: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    final_test()
