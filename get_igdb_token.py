#!/usr/bin/env python3
"""
IGDB Access Token Generator

This script helps you get a proper IGDB access token using the Twitch OAuth2 flow.
IGDB uses Twitch's authentication system.

IMPORTANT: This script will be deleted before pushing to GitHub.
"""

import requests
import os
import sys
from datetime import datetime, timedelta

def get_igdb_token(client_id, client_secret):
    """
    Get IGDB access token using Twitch OAuth2 flow
    
    Args:
        client_id (str): Your IGDB Client ID
        client_secret (str): Your IGDB Client Secret
    
    Returns:
        dict: Token response with access_token and expires_in
    """
    
    url = "https://id.twitch.tv/oauth2/token"
    
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    
    try:
        print(f"Requesting access token from Twitch...")
        response = requests.post(url, params=params, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"SUCCESS: Access token obtained!")
            print(f"   Token expires in: {token_data.get('expires_in', 'unknown')} seconds")
            print(f"   Token type: {token_data.get('token_type', 'unknown')}")
            
            # Calculate expiration time
            expires_in = token_data.get('expires_in', 0)
            if expires_in > 0:
                expiration_time = datetime.now() + timedelta(seconds=expires_in)
                print(f"   Expires at: {expiration_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return token_data
        else:
            print(f"ERROR: Failed to get access token")
            print(f"   Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def test_igdb_connection(client_id, access_token):
    """
    Test the IGDB API connection with the obtained token
    
    Args:
        client_id (str): Your IGDB Client ID
        access_token (str): The access token from get_igdb_token()
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    query = "fields name; limit 1;"
    
    try:
        print(f"\nTesting IGDB API connection...")
        response = requests.post(url, headers=headers, data=query, timeout=10)
        
        if response.status_code == 200:
            games = response.json()
            print(f"SUCCESS: IGDB API connection working!")
            print(f"   Found {len(games)} test game(s)")
            if games:
                print(f"   Sample game: {games[0].get('name', 'Unknown')}")
            return True
        else:
            print(f"ERROR: IGDB API test failed")
            print(f"   Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    """Main function to get and test IGDB token"""
    print("IGDB Access Token Generator")
    print("=" * 40)
    
    # Get credentials from user
    print("\nEnter your IGDB credentials:")
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("ERROR: Both Client ID and Client Secret are required")
        return
    
    print(f"\nClient ID: {client_id[:8]}...")
    print(f"Client Secret: {client_secret[:8]}...")
    
    # Get access token
    token_data = get_igdb_token(client_id, client_secret)
    
    if not token_data:
        print("\nFailed to get access token. Please check your credentials.")
        return
    
    access_token = token_data.get('access_token')
    
    # Test the token with IGDB API
    success = test_igdb_connection(client_id, access_token)
    
    if success:
        print(f"\nSUCCESS: Your IGDB setup is working!")
        print(f"\nTo use with ROM Cleanup Tool:")
        print(f"1. Set environment variables:")
        print(f"   export IGDB_CLIENT_ID='{client_id}'")
        print(f"   export IGDB_ACCESS_TOKEN='{access_token}'")
        print(f"\n2. Or use in GUI:")
        print(f"   - Run: python rom_cleanup_gui.py")
        print(f"   - Go to 'IGDB API' tab")
        print(f"   - Enter Client ID: {client_id}")
        print(f"   - Enter Access Token: {access_token}")
        
        print(f"\nNOTE: This token expires in {token_data.get('expires_in', 'unknown')} seconds")
        print(f"   You'll need to generate a new token when it expires.")
    else:
        print(f"\nIGDB API test failed. Please check your credentials.")


if __name__ == "__main__":
    main() 