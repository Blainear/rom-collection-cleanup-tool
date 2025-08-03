# Preview Changes Error Fix

## Issue
The GUI was throwing a `TypeError: ROMCleanupGUI.preview_changes() missing 1 required positional argument: 'to_remove'` error when the Preview Changes button was clicked.

## Root Cause
The error occurred because the `preview_changes` method was being called without the required `to_remove` parameter. This could happen in several scenarios:
1. An exception in the `find_duplicates_to_remove` method causing it to return None
2. A callback or event handler calling `preview_changes` directly without arguments
3. Race conditions or threading issues

## Solution
Made the following changes to make the code more robust:

### 1. Made `preview_changes` method more flexible
- Changed method signature from `preview_changes(self, to_remove)` to `preview_changes(self, to_remove=None)`
- Added logic to handle the case where `to_remove` is None or not provided
- If no argument is provided, the method now tries to get the data from the current state

### 2. Added defensive programming
- Added try-catch blocks around critical methods
- Added null checks for the `to_remove` parameter
- Added better error handling and logging

### 3. Simplified the button handler
- Updated `preview_changes_button` to call `preview_changes()` without arguments
- Let `preview_changes` handle getting the data from the current state

## Changes Made

### In `rom_cleanup_gui.py`:

1. **Line 580**: Changed method signature to accept default parameter
2. **Lines 581-590**: Added logic to handle None/empty cases
3. **Lines 607-618**: Simplified button handler
4. **Lines 620-690**: Added try-catch around `find_duplicates_to_remove`
5. **Lines 570-575**: Added try-catch around `preview_changes` call in scan method

## Testing
Created `test_preview_fix.py` to verify the fix works with various input scenarios.

## Result
The GUI should now handle the Preview Changes button click without throwing the TypeError, and provide better error messages if there are issues with the data. 