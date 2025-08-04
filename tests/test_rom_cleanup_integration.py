"""Integration tests for ROM cleanup functionality."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from rom_cleanup import scan_roms, find_duplicates_to_remove, move_to_safe_folder


class TestROMCleanupIntegration(unittest.TestCase):
    """Integration tests for ROM cleanup operations."""
    
    def setUp(self):
        """Set up test fixtures with temporary directory and ROM files."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test ROM files
        self.test_files = {
            "Super Mario Bros. (USA).nes": "usa",
            "Super Mario Bros. (Japan).nes": "japan", 
            "Super Mario Bros. (Europe).nes": "europe",
            "Final Fantasy (Japan).snes": "japan",
            "Sonic (USA).md": "usa",
            "Sonic (Europe).md": "europe",
            "Zelda no Densetsu (Japan).nes": "japan",  # Japanese-only
            "Secret of Mana (USA).snes": "usa",
            "Secret of Mana (Europe).snes": "europe",
            "Mario Kart (World).snes": "world",
        }
        
        # Create the test files
        for filename in self.test_files:
            file_path = self.temp_dir / filename
            file_path.write_text(f"Test ROM content for {filename}")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_scan_roms_groups_correctly(self):
        """Test that scan_roms groups ROM files correctly by base name."""
        rom_extensions = {".nes", ".snes", ".md"}
        
        with patch('rom_cleanup.load_game_cache'), \
             patch('rom_cleanup.save_game_cache'):
            
            result = scan_roms(str(self.temp_dir), rom_extensions)
            
            # Should group by base game name
            self.assertIn("Super Mario Bros.", result)
            self.assertIn("Final Fantasy", result)
            self.assertIn("Sonic", result)
            self.assertIn("Zelda no Densetsu", result)  # Japanese name
            self.assertIn("Secret of Mana", result)
            self.assertIn("Mario Kart", result)
            
            # Super Mario Bros should have 3 versions
            mario_files = result["Super Mario Bros."]
            self.assertEqual(len(mario_files), 3)
            
            # Check that regions are detected correctly
            regions = {item[1] for item in mario_files}
            self.assertEqual(regions, {"usa", "japan", "europe"})
    
    def test_find_duplicates_identifies_japanese_duplicates(self):
        """Test that find_duplicates_to_remove identifies Japanese duplicates correctly."""
        rom_extensions = {".nes", ".snes", ".md"}
        
        with patch('rom_cleanup.load_game_cache'), \
             patch('rom_cleanup.save_game_cache'):
            
            rom_groups = scan_roms(str(self.temp_dir), rom_extensions)
            to_remove = find_duplicates_to_remove(rom_groups)
            
            # Should identify Japanese duplicates where USA versions exist
            removed_names = [path.name for path in to_remove]
            
            # Should remove Japanese versions where USA exists
            self.assertIn("Super Mario Bros. (Japan).nes", removed_names)
            
            # Should NOT remove Japanese-only games
            self.assertNotIn("Zelda no Densetsu (Japan).nes", removed_names)
            
            # Should NOT remove USA versions
            self.assertNotIn("Super Mario Bros. (USA).nes", removed_names)
            self.assertNotIn("Sonic (USA).md", removed_names)
    
    def test_move_to_safe_folder_creates_structure(self):
        """Test that move_to_safe_folder creates proper directory structure."""
        # Create some files to move
        files_to_move = [
            self.temp_dir / "Super Mario Bros. (Japan).nes",
            self.temp_dir / "Final Fantasy (Japan).snes"
        ]
        
        moved_count = move_to_safe_folder(str(self.temp_dir), files_to_move)
        
        # Should have moved files
        self.assertEqual(moved_count, 2)
        
        # Check that to_delete folder was created
        to_delete_folder = self.temp_dir / "to_delete"
        self.assertTrue(to_delete_folder.exists())
        
        # Check that files were moved
        moved_mario = to_delete_folder / "Super Mario Bros. (Japan).nes"
        moved_ff = to_delete_folder / "Final Fantasy (Japan).snes"
        
        self.assertTrue(moved_mario.exists())
        self.assertTrue(moved_ff.exists())
        
        # Original files should be gone
        self.assertFalse((self.temp_dir / "Super Mario Bros. (Japan).nes").exists())
        self.assertFalse((self.temp_dir / "Final Fantasy (Japan).snes").exists())
    
    def test_full_cleanup_workflow(self):
        """Test the complete cleanup workflow from scan to move."""
        rom_extensions = {".nes", ".snes", ".md"}
        
        with patch('rom_cleanup.load_game_cache'), \
             patch('rom_cleanup.save_game_cache'):
            
            # 1. Scan ROMs
            rom_groups = scan_roms(str(self.temp_dir), rom_extensions)
            
            # 2. Find duplicates
            to_remove = find_duplicates_to_remove(rom_groups)
            
            # 3. Move to safe folder
            moved_count = move_to_safe_folder(str(self.temp_dir), to_remove)
            
            # Verify results
            self.assertGreater(moved_count, 0)
            
            # Check that Japanese duplicates were moved but Japanese-only were kept
            remaining_files = list(self.temp_dir.glob("*.nes"))
            remaining_names = [f.name for f in remaining_files]
            
            # Should keep USA versions
            self.assertIn("Super Mario Bros. (USA).nes", remaining_names)
            # Should keep Japanese-only
            self.assertIn("Zelda no Densetsu (Japan).nes", remaining_names)
            # Should NOT have Japanese duplicates
            self.assertNotIn("Super Mario Bros. (Japan).nes", remaining_names)
    
    def test_error_handling_invalid_directory(self):
        """Test error handling for invalid directory."""
        from rom_cleanup import validate_directory_path
        
        # Test empty path
        with self.assertRaises(ValueError):
            validate_directory_path("")
        
        # Test non-existent path
        with self.assertRaises(FileNotFoundError):
            validate_directory_path("/nonexistent/path")
        
        # Test file instead of directory
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("test")
        
        with self.assertRaises(NotADirectoryError):
            validate_directory_path(str(test_file))
    
    def test_scan_roms_with_subdirectories(self):
        """Test scanning ROMs in subdirectories."""
        # Create subdirectory with ROMs
        subdir = self.temp_dir / "Nintendo" / "NES"
        subdir.mkdir(parents=True)
        
        # Add ROM in subdirectory
        subdir_rom = subdir / "Metroid (USA).nes"
        subdir_rom.write_text("Test ROM in subdirectory")
        
        rom_extensions = {".nes", ".snes", ".md"}
        
        with patch('rom_cleanup.load_game_cache'), \
             patch('rom_cleanup.save_game_cache'):
            
            result = scan_roms(str(self.temp_dir), rom_extensions)
            
            # Should find ROM in subdirectory
            self.assertIn("Metroid", result)
            metroid_files = result["Metroid"]
            self.assertEqual(len(metroid_files), 1)
            
            # Path should include subdirectory
            file_path, region, original_name = metroid_files[0]
            self.assertTrue(str(file_path).endswith("Nintendo/NES/Metroid (USA).nes"))


class TestROMCleanupEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_directory(self):
        """Test behavior with empty directory."""
        rom_extensions = {".nes", ".snes"}
        
        with patch('rom_cleanup.load_game_cache'), \
             patch('rom_cleanup.save_game_cache'):
            
            result = scan_roms(str(self.temp_dir), rom_extensions)
            self.assertEqual(len(result), 0)
    
    def test_no_matching_extensions(self):
        """Test behavior when no files match ROM extensions."""
        # Create non-ROM files
        (self.temp_dir / "readme.txt").write_text("Not a ROM")
        (self.temp_dir / "image.jpg").write_text("Not a ROM")
        
        rom_extensions = {".nes", ".snes"}
        
        with patch('rom_cleanup.load_game_cache'), \
             patch('rom_cleanup.save_game_cache'):
            
            result = scan_roms(str(self.temp_dir), rom_extensions)
            self.assertEqual(len(result), 0)
    
    def test_malformed_rom_filenames(self):
        """Test handling of malformed ROM filenames."""
        # Create files with unusual names
        test_files = [
            "Game.nes",  # No region
            "Another Game (Unknown Region).nes",  # Unknown region
            "Game (USA) (Proto) (Beta).nes",  # Multiple tags
            "Game().nes",  # Empty parentheses
            ".hidden.nes",  # Hidden file
        ]
        
        for filename in test_files:
            (self.temp_dir / filename).write_text("Test ROM")
        
        rom_extensions = {".nes"}
        
        with patch('rom_cleanup.load_game_cache'), \
             patch('rom_cleanup.save_game_cache'):
            
            result = scan_roms(str(self.temp_dir), rom_extensions)
            
            # Should handle all files gracefully
            self.assertGreaterEqual(len(result), len(test_files))
    
    def test_permission_errors(self):
        """Test handling of permission errors during file operations."""
        # This test may not work on all systems due to permission restrictions
        test_file = self.temp_dir / "test.nes"
        test_file.write_text("Test ROM")
        
        with patch('shutil.move', side_effect=PermissionError("Permission denied")):
            result = move_to_safe_folder(str(self.temp_dir), [test_file])
            
            # Should handle permission error gracefully
            self.assertEqual(result, 0)  # No files moved due to permission error


if __name__ == "__main__":
    unittest.main()