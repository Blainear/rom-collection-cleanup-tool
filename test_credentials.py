#!/usr/bin/env python3
"""
Test script to verify credential management functionality.
"""

from credential_manager import get_credential_manager


def test_credential_manager():
    """Test the credential manager functionality."""
    print("=" * 50)
    print("Credential Manager Test")
    print("=" * 50)

    # Get the credential manager
    cm = get_credential_manager()

    # Test API key
    test_api_key = "a353d6c0655d0d57a818a6f8a4417da239e752c060bcb52cb27793dc49285112"

    print(f"Testing with API key: {test_api_key[:8]}...{test_api_key[-4:]}")

    # Store the credential
    print("Storing credential...")
    success = cm.store_credential("tgdb_api_key", test_api_key)
    print(f"Store success: {success}")

    # Retrieve the credential
    print("Retrieving credential...")
    retrieved_key = cm.get_credential("tgdb_api_key")
    print(
        f"Retrieved key: {retrieved_key[:8]}..."
        f"{retrieved_key[-4:] if retrieved_key else 'None'}"
    )

    # Check if they match
    if retrieved_key == test_api_key:
        print("✅ SUCCESS: Credential storage and retrieval working correctly!")
    else:
        print("❌ ERROR: Retrieved credential doesn't match stored credential")
        print(f"Expected: {test_api_key}")
        print(f"Got: {retrieved_key}")

    # List stored credentials
    print("\nListing stored credentials:")
    stored = cm.list_stored_credentials()
    for key, exists in stored.items():
        print(f"  {key}: {'✅' if exists else '❌'}")

    print("\n" + "=" * 50)
    print("Test Complete")
    print("=" * 50)


if __name__ == "__main__":
    test_credential_manager()
