#!/usr/bin/env python3
"""
Alternative IGDB API test - tries different endpoints and formats
"""

import requests
import json

def test_alternative_endpoints(client_id, access_token):
    """Test different IGDB API endpoints and request formats"""
    
    print("="*60)
    print("ALTERNATIVE IGDB API TESTS")
    print("="*60)
    
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    # Test 1: Original endpoint with different data format
    print("TEST 1: Original endpoint with JSON data")
    try:
        response = requests.post(
            'https://api.igdb.com/v4/games',
            headers=headers,
            json={'fields': 'name', 'limit': 1},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 2: Different endpoint
    print("TEST 2: Different endpoint - platforms")
    try:
        response = requests.post(
            'https://api.igdb.com/v4/platforms',
            headers=headers,
            data='fields name; limit 1;',
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 3: GET request instead of POST
    print("TEST 3: GET request to games endpoint")
    try:
        response = requests.get(
            'https://api.igdb.com/v4/games',
            headers=headers,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 4: Different data format
    print("TEST 4: Different data format")
    try:
        response = requests.post(
            'https://api.igdb.com/v4/games',
            headers=headers,
            data='fields name; where id = 1;',
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 5: Check if it's a content-type issue
    print("TEST 5: With explicit content-type")
    try:
        headers_with_content = headers.copy()
        headers_with_content['Content-Type'] = 'application/json'
        response = requests.post(
            'https://api.igdb.com/v4/games',
            headers=headers_with_content,
            data='fields name; limit 1;',
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Alternative IGDB API Tests")
    print("Enter your credentials when prompted:")
    print()
    
    client_id = input("Enter your IGDB Client ID: ").strip()
    access_token = input("Enter your IGDB Access Token: ").strip()
    
    if not client_id or not access_token:
        print("❌ Error: Both Client ID and Access Token are required")
    else:
        test_alternative_endpoints(client_id, access_token) 