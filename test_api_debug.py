#!/usr/bin/env python3
"""
Simple test script to debug IGDB API connection issues
"""

import requests
import json

def test_igdb_api(client_id, access_token):
    """Test IGDB API connection with detailed output"""
    
    print("="*60)
    print("IGDB API CONNECTION TEST")
    print("="*60)
    
    # Show credentials (masked)
    masked_client_id = client_id[:4] + "*" * (len(client_id) - 8) + client_id[-4:] if len(client_id) > 8 else "****"
    masked_access_token = access_token[:4] + "*" * (len(access_token) - 8) + access_token[-4:] if len(access_token) > 8 else "****"
    
    print(f"Client ID: {masked_client_id}")
    print(f"Access Token: {masked_access_token}")
    print()
    
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    print("Making API request...")
    print(f"URL: https://api.igdb.com/v4/games")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: fields name; limit 1;")
    print()
    
    try:
        response = requests.post(
            'https://api.igdb.com/v4/games',
            headers=headers,
            data='fields name; limit 1;',
            timeout=10
        )
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        # Try to get response body
        try:
            response_text = response.text
            print(f"Response Body: {response_text}")
        except Exception as e:
            print(f"Could not read response body: {e}")
        
        print()
        
        if response.status_code == 200:
            print("✅ SUCCESS: API connection working!")
            return True
        elif response.status_code == 401:
            print("❌ FAILED: Authentication failed (401)")
            print("This usually means:")
            print("  - Client ID is incorrect")
            print("  - Access Token is incorrect or expired")
            print("  - You need to regenerate your Access Token")
            return False
        elif response.status_code == 429:
            print("❌ FAILED: Rate limit exceeded (429)")
            print("Wait a few minutes and try again")
            return False
        else:
            print(f"❌ FAILED: Unexpected status code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ FAILED: Connection error - {e}")
        print("Check your internet connection")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ FAILED: Request timeout - {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {e}")
        return False

if __name__ == "__main__":
    print("IGDB API Debug Test")
    print("Enter your credentials when prompted:")
    print()
    
    client_id = input("Enter your IGDB Client ID: ").strip()
    access_token = input("Enter your IGDB Access Token: ").strip()
    
    if not client_id or not access_token:
        print("❌ Error: Both Client ID and Access Token are required")
    else:
        test_igdb_api(client_id, access_token) 