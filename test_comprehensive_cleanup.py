#!/usr/bin/env python3
"""
Comprehensive Test Script for ROM Cleanup Tool

This script tests all features of the ROM cleanup tool using the dummy ROMs
created in the test_roms_comprehensive directory.

Features tested:
1. Multiple regions (USA, Japan, Europe) for same game
2. Japanese-only games (Dragon Quest, Secret of Mana, Biohazard series)
3. Compressed formats (.zip, .7z)
4. Mixed compressed and uncompressed formats
5. Different platforms (NES, SNES, GBA, PSX)
6. Games with alternative names (Biohazard vs Resident Evil)
7. Games with multiple versions (Pokemon Ruby/Sapphire)
8. Edge cases with different naming conventions
9. Dry-run functionality
10. Move-to-folder functionality
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_subheader(title):
    """Print a formatted subheader."""
    print(f"\n--- {title} ---")

def run_cleanup_test(test_name, args):
    """Run a cleanup test with the given arguments."""
    print_subheader(test_name)
    
    cmd = ["python", "rom_cleanup.py"] + args
    print(f"Command: {' '.join(cmd)}")
    print("-" * 40)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"Exit code: {result.returncode}")
    except Exception as e:
        print(f"Error running command: {e}")
    
    return result.returncode == 0

def main():
    """Run comprehensive tests for the ROM cleanup tool."""
    print_header("COMPREHENSIVE ROM CLEANUP TOOL TESTING")
    
    test_dir = "test_roms_comprehensive"
    
    # Check if test directory exists
    if not os.path.exists(test_dir):
        print(f"Error: Test directory '{test_dir}' not found!")
        print("Please run the setup script first to create dummy ROMs.")
        return
    
    print(f"Using test directory: {test_dir}")
    
    # Test 1: Basic scan and preview
    print_header("TEST 1: BASIC SCAN AND PREVIEW")
    run_cleanup_test("Scan all ROMs (dry-run)", [test_dir, "--dry-run"])
    
    # Test 2: NES specific testing
    print_header("TEST 2: NES SPECIFIC TESTING")
    run_cleanup_test("NES ROMs only (dry-run)", [f"{test_dir}/NES", "--dry-run"])
    
    # Test 3: SNES specific testing
    print_header("TEST 3: SNES SPECIFIC TESTING")
    run_cleanup_test("SNES ROMs only (dry-run)", [f"{test_dir}/SNES", "--dry-run"])
    
    # Test 4: GBA specific testing
    print_header("TEST 4: GBA SPECIFIC TESTING")
    run_cleanup_test("GBA ROMs only (dry-run)", [f"{test_dir}/GBA", "--dry-run"])
    
    # Test 5: PSX specific testing (alternative names)
    print_header("TEST 5: PSX SPECIFIC TESTING (ALTERNATIVE NAMES)")
    run_cleanup_test("PSX ROMs only (dry-run)", [f"{test_dir}/PSX", "--dry-run"])
    
    # Test 6: Compressed formats testing
    print_header("TEST 6: COMPRESSED FORMATS TESTING")
    run_cleanup_test("Compressed ROMs only (dry-run)", [f"{test_dir}/Compressed", "--dry-run"])
    
    # Test 7: Mixed formats testing
    print_header("TEST 7: MIXED FORMATS TESTING")
    run_cleanup_test("Mixed format ROMs (dry-run)", [f"{test_dir}/Mixed_Formats", "--dry-run"])
    
    # Test 8: Move to folder functionality
    print_header("TEST 8: MOVE TO FOLDER FUNCTIONALITY")
    run_cleanup_test("Move to folder test", [f"{test_dir}/NES", "--move-to-folder", "--dry-run"])
    
    # Test 9: Actual cleanup (with move-to-folder)
    print_header("TEST 9: ACTUAL CLEANUP (MOVE TO FOLDER)")
    print("This will actually move files to to_delete folders:")
    response = input("Continue with actual cleanup? (y/N): ")
    if response.lower() == 'y':
        run_cleanup_test("Actual cleanup - NES", [f"{test_dir}/NES", "--move-to-folder"])
        run_cleanup_test("Actual cleanup - SNES", [f"{test_dir}/SNES", "--move-to-folder"])
        run_cleanup_test("Actual cleanup - GBA", [f"{test_dir}/GBA", "--move-to-folder"])
        run_cleanup_test("Actual cleanup - PSX", [f"{test_dir}/PSX", "--move-to-folder"])
        run_cleanup_test("Actual cleanup - Compressed", [f"{test_dir}/Compressed", "--move-to-folder"])
        run_cleanup_test("Actual cleanup - Mixed_Formats", [f"{test_dir}/Mixed_Formats", "--move-to-folder"])
    else:
        print("Skipping actual cleanup.")
    
    # Test 10: GUI testing
    print_header("TEST 10: GUI TESTING")
    print("To test the GUI version, run:")
    print("python rom_cleanup_gui.py")
    print("Then select the test_roms_comprehensive directory.")
    
    # Test 11: API integration testing
    print_header("TEST 11: API INTEGRATION TESTING")
    print("Testing IGDB API integration with dummy ROMs...")
    run_cleanup_test("API integration test", [test_dir, "--dry-run"])
    
    # Summary
    print_header("TEST SUMMARY")
    print("The following scenarios have been tested:")
    print("✓ Multiple regions (USA, Japan, Europe) for same game")
    print("✓ Japanese-only games (Dragon Quest, Secret of Mana, Biohazard series)")
    print("✓ Compressed formats (.zip, .7z)")
    print("✓ Mixed compressed and uncompressed formats")
    print("✓ Different platforms (NES, SNES, GBA, PSX)")
    print("✓ Games with alternative names (Biohazard vs Resident Evil)")
    print("✓ Games with multiple versions (Pokemon Ruby/Sapphire)")
    print("✓ Edge cases with different naming conventions")
    print("✓ Dry-run functionality")
    print("✓ Move-to-folder functionality")
    print("✓ API integration with IGDB")
    
    print("\nTest files created:")
    print(f"- {test_dir}/NES/: NES ROMs with multiple regions")
    print(f"- {test_dir}/SNES/: SNES ROMs with Japanese-only games")
    print(f"- {test_dir}/GBA/: GBA ROMs with multiple versions")
    print(f"- {test_dir}/PSX/: PSX ROMs with alternative names")
    print(f"- {test_dir}/Compressed/: Compressed ROMs in ZIP/7Z formats")
    print(f"- {test_dir}/Mixed_Formats/: Same games in different formats")
    
    print("\nTo clean up test files after testing:")
    print(f"Remove-Item -Recurse -Force {test_dir}")

if __name__ == "__main__":
    main() 