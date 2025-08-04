#!/usr/bin/env python3
"""
Test script to verify the duplicate detection fixes work correctly.

This tests:
1. Multi-disc games are preserved
2. Same-region variants are kept
3. Only cross-regional duplicates are removed
"""

import tempfile
from pathlib import Path
from rom_utils import get_base_name, is_multi_disc_game, get_version_info
from rom_cleanup import find_duplicates_to_remove


def test_multi_disc_preservation():
    """Test that multi-disc games are preserved."""
    print("🧪 Testing multi-disc game preservation...")
    
    # Test multi-disc detection
    multi_disc_files = [
        "Final Fantasy IX (USA) (Disc 1).bin",
        "Final Fantasy IX (USA) (Disc 2).bin", 
        "Final Fantasy IX (USA) (Disc 3).bin",
        "Final Fantasy IX (USA) (Disc 4).bin"
    ]
    
    assert is_multi_disc_game(multi_disc_files), "Should detect multi-disc game"
    
    # Test base name preservation
    for filename in multi_disc_files:
        base_name = get_base_name(filename)
        print(f"  {filename} → '{base_name}'")
        assert "Disc" in base_name, f"Disc info should be preserved in '{base_name}'"
    
    print("✅ Multi-disc preservation test passed!")


def test_same_region_preservation():
    """Test that same-region variants are preserved."""
    print("\\n🧪 Testing same-region preservation...")
    
    # Create test ROM groups - all Japan region
    temp_dir = Path(tempfile.mkdtemp())
    try:
        files = [
            temp_dir / "A Ressha de Ikou 4 - Evolution (Japan) (Gentei Set).zip",
            temp_dir / "A Ressha de Ikou 4 - Evolution (Japan) (Rev 1).zip",
            temp_dir / "A Ressha de Ikou 4 - Evolution (Japan).zip"
        ]
        
        # Create the files
        for f in files:
            f.touch()
        
        # Create ROM groups
        rom_groups = {
            "A Ressha de Ikou 4 - Evolution": [
                (files[0], "japan", "A Ressha de Ikou 4 - Evolution (Japan) (Gentei Set).zip"),
                (files[1], "japan", "A Ressha de Ikou 4 - Evolution (Japan) (Rev 1).zip"),
                (files[2], "japan", "A Ressha de Ikou 4 - Evolution (Japan).zip")
            ]
        }
        
        # Test duplicate detection
        to_remove = find_duplicates_to_remove(rom_groups)
        
        print(f"  Files to remove: {len(to_remove)}")
        assert len(to_remove) == 0, "Should NOT remove same-region files"
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("✅ Same-region preservation test passed!")


def test_cross_regional_removal():
    """Test that cross-regional duplicates are correctly removed."""
    print("\\n🧪 Testing cross-regional duplicate removal...")
    
    temp_dir = Path(tempfile.mkdtemp())
    try:
        files = [
            temp_dir / "Biohazard (Japan).zip",
            temp_dir / "Resident Evil (USA).zip"
        ]
        
        # Create the files
        for f in files:
            f.touch()
        
        # Create ROM groups - same canonical name, different regions
        rom_groups = {
            "Resident Evil": [
                (files[0], "japan", "Biohazard (Japan).zip"),
                (files[1], "usa", "Resident Evil (USA).zip")
            ]
        }
        
        # Test duplicate detection
        to_remove = find_duplicates_to_remove(rom_groups)
        
        print(f"  Files to remove: {len(to_remove)}")
        assert len(to_remove) == 1, "Should remove 1 file (Japanese version)"
        
        removed_file = to_remove[0]
        print(f"  Removed file: {removed_file.name}")
        assert "Biohazard" in removed_file.name, f"Should remove Japanese version, got: {removed_file.name}"
        # The file path should be the Japanese file
        assert removed_file.name == "Biohazard (Japan).zip", f"Should remove Japanese file, got: {removed_file.name}"
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("✅ Cross-regional removal test passed!")


def test_version_info_extraction():
    """Test version information extraction."""
    print("\\n🧪 Testing version info extraction...")
    
    test_cases = [
        ("Game (Japan) (Rev 1).zip", "Rev 1"),
        ("Game (USA) (Special Edition).zip", "Special Edition"),
        ("Game (Europe) (Gentei Set).zip", "Gentei Set"),
        ("Game (World).zip", ""),
        ("Game (Japan) (Rev 2) (Beta).zip", "Rev 2 Beta")
    ]
    
    for filename, expected in test_cases:
        version_info = get_version_info(filename)
        print(f"  {filename} → '{version_info}'")
        assert expected in version_info or (not expected and not version_info), \
               f"Expected '{expected}' in '{version_info}'"
    
    print("✅ Version info extraction test passed!")


def main():
    """Run all tests."""
    print("🔧 Testing ROM cleanup fixes...")
    print("=" * 50)
    
    test_multi_disc_preservation()
    test_same_region_preservation()
    test_cross_regional_removal()
    test_version_info_extraction()
    
    print("\\n" + "=" * 50)
    print("🎉 All tests passed! The fixes are working correctly.")
    print("\\nThe tool will now:")
    print("✅ Preserve all discs of multi-disc games")
    print("✅ Keep same-region variants (Rev 1, Special Editions, etc.)")
    print("✅ Only remove cross-regional duplicates (Japan when USA exists)")


if __name__ == "__main__":
    main()