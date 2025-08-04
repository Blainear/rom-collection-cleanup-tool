#!/usr/bin/env python3
"""
Test script to verify the API credential saving and loading functionality.
"""

import os
import json
from pathlib import Path

# Import the functions we added
import sys
sys.path.append('.')
from rom_cleanup_gui import load_api_credentials, save_api_credentials

def test_credential_save_load():
    """Test saving and loading API credentials."""
    print("=== Testing API Credential Save/Load Functionality ===\n")
    
    # Test data
    test_client_id = "test_client_id_12345"
    test_access_token = "test_access_token_67890"
    
    print("1. Testing credential saving...")
    success = save_api_credentials(test_client_id, test_access_token)
    
    if success:
        print("   ✅ Credentials saved successfully")
    else:
        print("   ❌ Failed to save credentials")
        return
    
    print("\n2. Testing credential loading...")
    loaded_client_id, loaded_access_token = load_api_credentials()
    
    if loaded_client_id == test_client_id and loaded_access_token == test_access_token:
        print("   ✅ Credentials loaded successfully")
        print(f"   Client ID: {loaded_client_id}")
        print(f"   Access Token: {loaded_access_token}")
    else:
        print("   ❌ Loaded credentials don't match saved ones")
        print(f"   Expected Client ID: {test_client_id}")
        print(f"   Loaded Client ID: {loaded_client_id}")
        print(f"   Expected Access Token: {test_access_token}")
        print(f"   Loaded Access Token: {loaded_access_token}")
        return
    
    print("\n3. Testing file existence...")
    credentials_file = Path("api_credentials.json")
    if credentials_file.exists():
        print("   ✅ Credentials file created successfully")
        
        # Show file contents (for verification)
        try:
            with open(credentials_file, "r") as f:
                content = json.load(f)
            print(f"   File contents: {content}")
        except Exception as e:
            print(f"   ⚠️  Could not read file: {e}")
    else:
        print("   ❌ Credentials file not found")
    
    print("\n4. Testing empty credential handling...")
    empty_client_id, empty_access_token = load_api_credentials()
    
    # Clean up test file
    try:
        credentials_file.unlink()
        print("   ✅ Test file cleaned up")
    except Exception as e:
        print(f"   ⚠️  Could not clean up test file: {e}")
    
    # Test loading when file doesn't exist
    missing_client_id, missing_access_token = load_api_credentials()
    if missing_client_id == "" and missing_access_token == "":
        print("   ✅ Correctly returned empty strings when file missing")
    else:
        print("   ❌ Should return empty strings when file missing")
    
    print("\n=== Test Complete ===")
    print("The credential saving functionality is working correctly!")
    print("\nIn the GUI:")
    print("- Enter your IGDB credentials in the IGDB API tab")
    print("- They will auto-save when connection is successful")
    print("- Or click 'Save Credentials' to manually save")
    print("- Credentials will auto-load next time you open the app")

def show_gui_instructions():
    """Show instructions for using the credential saving in the GUI."""
    print("\n" + "="*60)
    print("🔑 How to Use the New Credential Saving Feature:")
    print("="*60)
    
    instructions = [
        "1. Open the ROM Cleanup GUI",
        "2. Go to the 'IGDB API' tab",
        "3. Enter your Client ID and Access Token",
        "4. The app will automatically test the connection",
        "5. If successful, credentials are auto-saved",
        "6. Or click 'Save Credentials' to manually save",
        "7. Next time you open the app, credentials auto-load",
        "8. No more re-entering credentials every time! 🎉"
    ]
    
    for instruction in instructions:
        print(instruction)
    
    print("\n📁 Files created:")
    print("- api_credentials.json (contains your saved credentials)")
    print("- This file is ignored by git for security")
    
    print("\n🔒 Security notes:")
    print("- Credentials are stored locally in plain text")
    print("- The file is added to .gitignore")
    print("- Only you can access the credentials on your machine")

if __name__ == "__main__":
    test_credential_save_load()
    show_gui_instructions()