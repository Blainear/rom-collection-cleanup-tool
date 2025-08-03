#!/usr/bin/env python3
"""
Script to generate IGDB App Access Token
"""

import requests
import json

def generate_igdb_token(client_id, client_secret):
    """Generate IGDB App Access Token"""
    
    print("="*60)
    print("GENERATING IGDB APP ACCESS TOKEN")
    print("="*60)
    
    url = f"https://id.twitch.tv/oauth2/token"
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    
    try:
        response = requests.post(url, params=params)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! Your App Access Token:")
            print(f"Access Token: {data['access_token']}")
            print(f"Expires in: {data['expires_in']} seconds")
            print(f"Token Type: {data['token_type']}")
            print()
            print("Use this Access Token in your ROM Cleanup Tool!")
            return data['access_token']
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

if __name__ == "__main__":
    print("IGDB Token Generator")
    print("Enter your credentials when prompted:")
    print()
    
    client_id = input("Enter your IGDB Client ID: ").strip()
    client_secret = input("Enter your IGDB Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Error: Both Client ID and Client Secret are required")
    else:
        generate_igdb_token(client_id, client_secret) 