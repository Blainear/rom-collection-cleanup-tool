"""
Tests for the configuration module.
"""

import pytest
from pathlib import Path
import tempfile
import os

from config import CleanupConfig, ProcessingStats


class TestCleanupConfig:
    """Test cases for CleanupConfig dataclass."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        config = CleanupConfig()
        assert config.rom_directory == ""
        assert config.operation_mode == "move"
        assert config.region_priority == "usa"
        assert config.keep_japanese_only is True
        assert config.keep_europe_only is True
        
    def test_get_rom_extensions_default(self):
        """Test default ROM extensions."""
        config = CleanupConfig()
        extensions = config.get_rom_extensions()
        assert '.nes' in extensions
        assert '.snes' in extensions
        assert '.zip' in extensions
        assert '.iso' in extensions
        
    def test_get_rom_extensions_custom(self):
        """Test custom ROM extensions."""
        config = CleanupConfig(custom_extensions="abc, .def, xyz")
        extensions = config.get_rom_extensions()
        assert '.abc' in extensions
        assert '.def' in extensions
        assert '.xyz' in extensions
        assert '.nes' in extensions  # Default extensions should still be included
        
    def test_validate_valid_config(self):
        """Test validation with valid configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = CleanupConfig(
                rom_directory=temp_dir,
                operation_mode="move",
                region_priority="usa"
            )
            assert config.validate() is True
            
    def test_validate_invalid_directory(self):
        """Test validation with invalid directory."""
        config = CleanupConfig(rom_directory="/nonexistent/directory")
        assert config.validate() is False
        
    def test_validate_empty_directory(self):
        """Test validation with empty directory."""
        config = CleanupConfig()
        assert config.validate() is False
        
    def test_validate_invalid_operation_mode(self):
        """Test validation with invalid operation mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = CleanupConfig(
                rom_directory=temp_dir,
                operation_mode="invalid_mode"
            )
            assert config.validate() is False
            
    def test_validate_invalid_region_priority(self):
        """Test validation with invalid region priority."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = CleanupConfig(
                rom_directory=temp_dir,
                region_priority="invalid_region"
            )
            assert config.validate() is False


class TestProcessingStats:
    """Test cases for ProcessingStats dataclass."""
    
    def test_default_values(self):
        """Test that default values are zero."""
        stats = ProcessingStats()
        assert stats.total_files_scanned == 0
        assert stats.total_games_found == 0
        assert stats.duplicates_found == 0
        assert stats.files_processed == 0
        assert stats.files_moved == 0
        assert stats.files_deleted == 0
        assert stats.errors_encountered == 0
        
    def test_reset_stats(self):
        """Test resetting statistics."""
        stats = ProcessingStats(
            total_files_scanned=100,
            total_games_found=50,
            duplicates_found=10,
            files_processed=5,
            files_moved=3,
            files_deleted=2,
            errors_encountered=1
        )
        
        # Verify values are set
        assert stats.total_files_scanned == 100
        assert stats.duplicates_found == 10
        
        # Reset and verify all are zero
        stats.reset()
        assert stats.total_files_scanned == 0
        assert stats.total_games_found == 0
        assert stats.duplicates_found == 0
        assert stats.files_processed == 0
        assert stats.files_moved == 0
        assert stats.files_deleted == 0
        assert stats.errors_encountered == 0