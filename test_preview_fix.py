#!/usr/bin/env python3
"""
Test script to verify the preview_changes fix
"""

import tkinter as tk
from rom_cleanup_gui import ROMCleanupGUI

def test_preview_changes():
    """Test that preview_changes works with and without arguments"""
    root = tk.Tk()
    app = ROMCleanupGUI(root)
    
    # Test 1: Call with None (should work now)
    print("Test 1: Calling preview_changes with None")
    try:
        app.preview_changes(None)
        print("✓ Test 1 passed")
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
    
    # Test 2: Call without arguments (should work now)
    print("Test 2: Calling preview_changes without arguments")
    try:
        app.preview_changes()
        print("✓ Test 2 passed")
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
    
    # Test 3: Call with empty list
    print("Test 3: Calling preview_changes with empty list")
    try:
        app.preview_changes([])
        print("✓ Test 3 passed")
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")
    
    root.destroy()
    print("All tests completed!")

if __name__ == "__main__":
    test_preview_changes() 