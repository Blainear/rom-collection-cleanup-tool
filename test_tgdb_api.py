#!/usr/bin/env python3
"""
Simple test script to verify TheGamesDB API key functionality.
"""

import json

import requests


def test_tgdb_api(api_key):
    """Test TheGamesDB API with the provided key."""
    print(f"Testing TheGamesDB API with key: {api_key[:8]}...{api_key[-4:]}")

    try:
        # Test the API with a simple request
        url = "https://api.thegamesdb.net/v1/Games/ByGameName"
        params = {"apikey": api_key, "name": "Mario", "fields": "games"}

        print("Making API request...")
        response = requests.get(url, params=params, timeout=10)

        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: API connection successful!")
            print(f"Response data keys: {list(data.keys())}")

            if data.get("data") and data["data"].get("games"):
                games = data["data"]["games"]
                print(f"Found {len(games)} games")
                if games:
                    print(f"First game: {games[0].get('game_title', 'Unknown')}")
            else:
                print("WARNING: API responded but no games found in response")
                print(f"Full response: {json.dumps(data, indent=2)}")

        elif response.status_code == 401:
            print("ERROR: Authentication failed (401)")
            print("This means the API key is invalid or expired")
            print(f"Response text: {response.text}")

        elif response.status_code == 429:
            print("ERROR: Rate limit exceeded (429)")
            print("Too many requests - wait a moment and try again")

        else:
            print(f"ERROR: Unexpected response code: {response.status_code}")
            print(f"Response text: {response.text}")

    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Connection error: {e}")
        print("Check your internet connection")

    except requests.exceptions.Timeout as e:
        print(f"ERROR: Request timeout: {e}")
        print("The API request took too long")

    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")


if __name__ == "__main__":
    # Your API key
    api_key = "a353d6c0655d0d57a818a6f8a4417da239e752c060bcb52cb27793dc49285112"

    print("=" * 50)
    print("TheGamesDB API Key Test")
    print("=" * 50)

    test_tgdb_api(api_key)

    print("\n" + "=" * 50)
    print("Test Complete")
    print("=" * 50)
