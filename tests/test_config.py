"""Tests for config module."""

import tempfile
import unittest
from pathlib import Path

from config import CleanupConfig, ProcessingStats


class TestCleanupConfig(unittest.TestCase):
    """Test cases for CleanupConfig class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        config = CleanupConfig()
        
        self.assertEqual(config.rom_directory, "")
        self.assertTrue(config.preserve_subdirs)
        self.assertEqual(config.operation_mode, "move")
        self.assertEqual(config.region_priority, "usa")
        self.assertTrue(config.keep_japanese_only)
        self.assertTrue(config.keep_europe_only)
        self.assertEqual(config.custom_extensions, "")
        self.assertFalse(config.create_backup)
        self.assertEqual(config.backup_directory, "")
        self.assertEqual(config.igdb_client_id, "")
        self.assertEqual(config.igdb_access_token, "")
        self.assertFalse(config.dry_run)
        self.assertTrue(config.move_to_folder)
    
    def test_get_rom_extensions_default(self):
        """Test getting default ROM extensions."""
        config = CleanupConfig()
        extensions = config.get_rom_extensions()
        
        # Should include common ROM extensions
        self.assertIn(".nes", extensions)
        self.assertIn(".snes", extensions)
        self.assertIn(".gb", extensions)
        self.assertIn(".gba", extensions)
        self.assertIn(".zip", extensions)
        self.assertIn(".iso", extensions)
        
        # Should be a reasonable number of extensions
        self.assertGreater(len(extensions), 50)
    
    def test_get_rom_extensions_with_custom(self):
        """Test getting ROM extensions with custom additions."""
        config = CleanupConfig()
        config.custom_extensions = "rom, bin,  .chd"  # Mixed formats
        
        extensions = config.get_rom_extensions()
        
        # Should include custom extensions
        self.assertIn(".rom", extensions)
        self.assertIn(".bin", extensions)
        self.assertIn(".chd", extensions)
        
        # Should still include defaults
        self.assertIn(".nes", extensions)
        self.assertIn(".snes", extensions)
    
    def test_get_rom_extensions_normalizes_format(self):
        """Test that custom extensions are normalized correctly."""
        config = CleanupConfig()
        config.custom_extensions = "ROM, .BIN, chd, .ISO"  # Mixed case and dots
        
        extensions = config.get_rom_extensions()
        
        # Should normalize to lowercase with dots
        self.assertIn(".rom", extensions)
        self.assertIn(".bin", extensions)
        self.assertIn(".chd", extensions)
        self.assertIn(".iso", extensions)  # .iso should appear twice (default + custom)
    
    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        config = CleanupConfig()
        config.rom_directory = str(self.temp_dir)
        config.operation_mode = "move"
        config.region_priority = "usa"
        
        self.assertTrue(config.validate())
    
    def test_validate_empty_directory(self):
        """Test validation fails with empty directory."""
        config = CleanupConfig()
        config.rom_directory = ""
        
        self.assertFalse(config.validate())
    
    def test_validate_nonexistent_directory(self):
        """Test validation fails with nonexistent directory."""
        config = CleanupConfig()
        config.rom_directory = "/nonexistent/directory"
        
        self.assertFalse(config.validate())
    
    def test_validate_invalid_operation_mode(self):
        """Test validation fails with invalid operation mode."""
        config = CleanupConfig()
        config.rom_directory = str(self.temp_dir)
        config.operation_mode = "invalid_mode"
        
        self.assertFalse(config.validate())
    
    def test_validate_invalid_region_priority(self):
        """Test validation fails with invalid region priority."""
        config = CleanupConfig()
        config.rom_directory = str(self.temp_dir)
        config.region_priority = "invalid_region"
        
        self.assertFalse(config.validate())
    
    def test_all_operation_modes_valid(self):
        """Test that all expected operation modes are valid."""
        config = CleanupConfig()
        config.rom_directory = str(self.temp_dir)
        
        valid_modes = ["move", "delete", "backup"]
        for mode in valid_modes:
            config.operation_mode = mode
            self.assertTrue(config.validate(), f"Mode '{mode}' should be valid")
    
    def test_all_region_priorities_valid(self):
        """Test that all expected region priorities are valid."""
        config = CleanupConfig()
        config.rom_directory = str(self.temp_dir)
        
        valid_regions = ["usa", "europe", "japan", "world"]
        for region in valid_regions:
            config.region_priority = region
            self.assertTrue(config.validate(), f"Region '{region}' should be valid")


class TestProcessingStats(unittest.TestCase):
    """Test cases for ProcessingStats class."""
    
    def test_default_values(self):
        """Test that default values are zero."""
        stats = ProcessingStats()
        
        self.assertEqual(stats.total_files_scanned, 0)
        self.assertEqual(stats.total_games_found, 0)
        self.assertEqual(stats.duplicates_found, 0)
        self.assertEqual(stats.files_processed, 0)
        self.assertEqual(stats.files_moved, 0)
        self.assertEqual(stats.files_deleted, 0)
        self.assertEqual(stats.errors_encountered, 0)
    
    def test_setting_values(self):
        """Test setting various statistic values."""
        stats = ProcessingStats()
        
        stats.total_files_scanned = 100
        stats.total_games_found = 50
        stats.duplicates_found = 25
        stats.files_processed = 25
        stats.files_moved = 20
        stats.files_deleted = 5
        stats.errors_encountered = 2
        
        self.assertEqual(stats.total_files_scanned, 100)
        self.assertEqual(stats.total_games_found, 50)
        self.assertEqual(stats.duplicates_found, 25)
        self.assertEqual(stats.files_processed, 25)
        self.assertEqual(stats.files_moved, 20)
        self.assertEqual(stats.files_deleted, 5)
        self.assertEqual(stats.errors_encountered, 2)
    
    def test_reset(self):
        """Test that reset method clears all statistics."""
        stats = ProcessingStats()
        
        # Set some values
        stats.total_files_scanned = 100
        stats.total_games_found = 50
        stats.duplicates_found = 25
        stats.files_processed = 25
        stats.files_moved = 20
        stats.files_deleted = 5
        stats.errors_encountered = 2
        
        # Reset
        stats.reset()
        
        # All should be zero
        self.assertEqual(stats.total_files_scanned, 0)
        self.assertEqual(stats.total_games_found, 0)
        self.assertEqual(stats.duplicates_found, 0)
        self.assertEqual(stats.files_processed, 0)
        self.assertEqual(stats.files_moved, 0)
        self.assertEqual(stats.files_deleted, 0)
        self.assertEqual(stats.errors_encountered, 0)
    
    def test_initialization_with_values(self):
        """Test initializing ProcessingStats with specific values."""
        stats = ProcessingStats(
            total_files_scanned=200,
            total_games_found=100,
            duplicates_found=50,
            files_processed=45,
            files_moved=40,
            files_deleted=5,
            errors_encountered=1
        )
        
        self.assertEqual(stats.total_files_scanned, 200)
        self.assertEqual(stats.total_games_found, 100)
        self.assertEqual(stats.duplicates_found, 50)
        self.assertEqual(stats.files_processed, 45)
        self.assertEqual(stats.files_moved, 40)
        self.assertEqual(stats.files_deleted, 5)
        self.assertEqual(stats.errors_encountered, 1)


class TestConfigIntegration(unittest.TestCase):
    """Integration tests for config classes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create some test ROM files
        (self.temp_dir / "game1.nes").write_text("test")
        (self.temp_dir / "game2.snes").write_text("test")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_with_real_directory(self):
        """Test configuration validation with real directory."""
        config = CleanupConfig()
        config.rom_directory = str(self.temp_dir)
        
        # Should validate successfully
        self.assertTrue(config.validate())
        
        # Extensions should work
        extensions = config.get_rom_extensions()
        self.assertIn(".nes", extensions)
        self.assertIn(".snes", extensions)
    
    def test_config_edge_cases(self):
        """Test configuration edge cases."""
        config = CleanupConfig()
        
        # Empty custom extensions should not break anything
        config.custom_extensions = ""
        extensions = config.get_rom_extensions()
        self.assertGreater(len(extensions), 0)
        
        # Whitespace-only custom extensions
        config.custom_extensions = "   "
        extensions = config.get_rom_extensions()
        self.assertGreater(len(extensions), 0)
        
        # Duplicate extensions should be handled
        config.custom_extensions = "nes, .nes, NES"
        extensions = config.get_rom_extensions()
        # Should only have one .nes entry (case insensitive)
        nes_count = sum(1 for ext in extensions if ext.lower() == ".nes")
        self.assertEqual(nes_count, 1)


if __name__ == "__main__":
    unittest.main()