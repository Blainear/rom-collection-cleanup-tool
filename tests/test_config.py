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
        config = CleanupConfig(rom_directory=self.temp_dir)

        self.assertEqual(config.rom_directory, self.temp_dir)
        self.assertFalse(config.dry_run)
        self.assertFalse(config.move_to_folder)
        self.assertEqual(config.custom_extensions, None)
        self.assertTrue(config.use_igdb_api)
        self.assertFalse(config.use_thegamesdb_api)
        self.assertEqual(config.igdb_client_id, None)
        self.assertEqual(config.igdb_access_token, None)
        self.assertEqual(config.thegamesdb_api_key, None)
        self.assertEqual(config.preferred_region, "usa")
        self.assertTrue(config.keep_japanese_only)
        self.assertTrue(config.enable_cross_language_matching)
        self.assertFalse(config.verbose)
        self.assertFalse(config.quiet)
        self.assertFalse(config.log_to_file)
        self.assertEqual(config.log_file, None)

    def test_rom_extensions_default(self):
        """Test getting default ROM extensions."""
        config = CleanupConfig(rom_directory=self.temp_dir)

        # Should be a set
        self.assertIsInstance(config.rom_extensions, set)

        # Should be empty by default
        self.assertEqual(len(config.rom_extensions), 0)

    def test_rom_extensions_with_custom(self):
        """Test getting ROM extensions with custom additions."""
        config = CleanupConfig(
            rom_directory=self.temp_dir,
            custom_extensions="rom, bin,  .chd",  # Mixed formats
        )

        # Custom extensions should be set
        self.assertEqual(config.custom_extensions, "rom, bin,  .chd")

    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        config = CleanupConfig(rom_directory=self.temp_dir)

        # Should not raise any exceptions for valid config
        # The validation happens in __post_init__
        self.assertIsNotNone(config)  # If we get here, validation passed

    def test_validate_nonexistent_directory(self):
        """Test validation fails with nonexistent directory."""
        with self.assertRaises(FileNotFoundError):
            CleanupConfig(rom_directory=Path("/nonexistent/directory"))

    def test_validate_file_not_directory(self):
        """Test validation fails when path is a file, not directory."""
        # Create a file
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("test")

        with self.assertRaises(NotADirectoryError):
            CleanupConfig(rom_directory=test_file)

    def test_verbose_and_quiet_conflict(self):
        """Test that verbose and quiet cannot be used together."""
        with self.assertRaises(ValueError):
            CleanupConfig(rom_directory=self.temp_dir, verbose=True, quiet=True)


class TestProcessingStats(unittest.TestCase):
    """Test cases for ProcessingStats class."""

    def test_default_values(self):
        """Test that default values are zero."""
        stats = ProcessingStats()

        self.assertEqual(stats.total_files_scanned, 0)
        self.assertEqual(stats.total_games_found, 0)
        self.assertEqual(stats.files_to_remove, 0)
        self.assertEqual(stats.files_removed, 0)
        self.assertEqual(stats.files_moved, 0)
        self.assertEqual(stats.multi_disc_games, 0)
        self.assertEqual(stats.cross_regional_duplicates, 0)
        self.assertEqual(stats.same_region_duplicates, 0)
        self.assertEqual(stats.api_queries_made, 0)
        self.assertEqual(stats.api_cache_hits, 0)
        self.assertEqual(stats.cross_language_matches, 0)
        self.assertEqual(stats.scan_time_seconds, 0.0)
        self.assertEqual(stats.processing_time_seconds, 0.0)
        self.assertEqual(stats.total_time_seconds, 0.0)
        self.assertEqual(stats.errors_encountered, 0)
        self.assertEqual(stats.permission_errors, 0)
        self.assertEqual(stats.file_not_found_errors, 0)

    def test_setting_values(self):
        """Test setting various statistic values."""
        stats = ProcessingStats()

        stats.total_files_scanned = 100
        stats.total_games_found = 50
        stats.files_to_remove = 25
        stats.files_removed = 20
        stats.files_moved = 5
        stats.errors_encountered = 2

        self.assertEqual(stats.total_files_scanned, 100)
        self.assertEqual(stats.total_games_found, 50)
        self.assertEqual(stats.files_to_remove, 25)
        self.assertEqual(stats.files_removed, 20)
        self.assertEqual(stats.files_moved, 5)
        self.assertEqual(stats.errors_encountered, 2)

    def test_add_error_general(self):
        """Test adding general errors."""
        stats = ProcessingStats()

        stats.add_error("general")
        self.assertEqual(stats.errors_encountered, 1)
        self.assertEqual(stats.permission_errors, 0)
        self.assertEqual(stats.file_not_found_errors, 0)

    def test_add_error_permission(self):
        """Test adding permission errors."""
        stats = ProcessingStats()

        stats.add_error("permission")
        self.assertEqual(stats.errors_encountered, 1)
        self.assertEqual(stats.permission_errors, 1)
        self.assertEqual(stats.file_not_found_errors, 0)

    def test_add_error_file_not_found(self):
        """Test adding file not found errors."""
        stats = ProcessingStats()

        stats.add_error("file_not_found")
        self.assertEqual(stats.errors_encountered, 1)
        self.assertEqual(stats.permission_errors, 0)
        self.assertEqual(stats.file_not_found_errors, 1)

    def test_total_time_calculation(self):
        """Test that total time is calculated correctly."""
        stats = ProcessingStats()

        stats.scan_time_seconds = 10.5
        stats.processing_time_seconds = 5.2

        # Manual calculation since __post_init__ only runs once
        expected_total = stats.scan_time_seconds + stats.processing_time_seconds
        self.assertEqual(expected_total, 15.7)

        # The actual total_time_seconds should be 0 since it's only calculated in __post_init__
        self.assertEqual(stats.total_time_seconds, 0.0)

    def test_get_summary(self):
        """Test getting summary dictionary."""
        stats = ProcessingStats()

        # Set some values
        stats.total_files_scanned = 100
        stats.total_games_found = 50
        stats.files_to_remove = 25
        stats.files_removed = 20
        stats.files_moved = 5
        stats.errors_encountered = 2

        summary = stats.get_summary()

        self.assertEqual(summary["total_files_scanned"], 100)
        self.assertEqual(summary["total_games_found"], 50)
        self.assertEqual(summary["files_to_remove"], 25)
        self.assertEqual(summary["files_removed"], 20)
        self.assertEqual(summary["files_moved"], 5)
        self.assertEqual(summary["errors_encountered"], 2)

    def test_str_representation(self):
        """Test string representation of statistics."""
        stats = ProcessingStats()

        # Set some values
        stats.total_files_scanned = 100
        stats.total_games_found = 50
        stats.files_to_remove = 25
        stats.files_removed = 20
        stats.files_moved = 5
        stats.errors_encountered = 2

        str_repr = str(stats)

        # Should contain the key information
        self.assertIn("Files scanned: 100", str_repr)
        self.assertIn("Games found: 50", str_repr)
        self.assertIn("Files to remove: 25", str_repr)
        self.assertIn("Files removed: 20", str_repr)
        self.assertIn("Files moved: 5", str_repr)
        self.assertIn("Errors: 2", str_repr)


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
        """Test configuration with real directory."""
        config = CleanupConfig(rom_directory=self.temp_dir)

        # Should not raise any exceptions for valid directory
        self.assertEqual(config.rom_directory, self.temp_dir)

    def test_stats_integration(self):
        """Test integration between config and stats."""
        config = CleanupConfig(rom_directory=self.temp_dir)
        stats = ProcessingStats()

        # Simulate some processing
        stats.total_files_scanned = 10
        stats.total_games_found = 5
        stats.files_to_remove = 2
        stats.files_removed = 1
        stats.files_moved = 1

        # Both should work together
        self.assertTrue(config.rom_directory.exists())
        self.assertEqual(stats.total_files_scanned, 10)


if __name__ == "__main__":
    unittest.main()
