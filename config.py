"""Configuration classes for ROM cleanup tool.

This module provides structured configuration classes for better
organization of settings and parameters. The default ROM extensions and
platform mappings are imported from :mod:`rom_constants` to avoid
duplication across the codebase.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Set

from rom_constants import ROM_EXTENSIONS


@dataclass
class CleanupConfig:
    """Configuration for ROM cleanup operations."""

    # Directory settings
    rom_directory: str = ""
    preserve_subdirs: bool = True

    # Operation settings
    operation_mode: str = "move"  # move, delete, backup
    region_priority: str = "usa"  # usa, europe, japan, world

    # Filtering options
    keep_japanese_only: bool = True
    keep_europe_only: bool = True
    custom_extensions: str = ""

    # Backup settings
    create_backup: bool = False
    backup_directory: str = ""

    # API settings
    igdb_client_id: str = ""
    igdb_access_token: str = ""

    # Processing settings
    dry_run: bool = False
    move_to_folder: bool = True

    def get_rom_extensions(self) -> Set[str]:
        """Return the set of ROM file extensions to process."""

        default_extensions = set(ROM_EXTENSIONS)

        if self.custom_extensions:
            custom_exts: Set[str] = set()
            for ext in self.custom_extensions.split(","):
                ext = ext.strip().lower()
                ext = ext if ext.startswith(".") else "." + ext
                custom_exts.add(ext)
            default_extensions.update(custom_exts)

        return default_extensions

    def validate(self) -> bool:
        """Validate the configuration settings."""
        if not self.rom_directory:
            return False

        if not Path(self.rom_directory).exists():
            return False

        if self.operation_mode not in ["move", "delete", "backup"]:
            return False

        if self.region_priority not in ["usa", "europe", "japan", "world"]:
            return False

        return True


@dataclass
class ProcessingStats:
    """Statistics from ROM processing operations."""

    total_files_scanned: int = 0
    total_games_found: int = 0
    duplicates_found: int = 0
    files_processed: int = 0
    files_moved: int = 0
    files_deleted: int = 0
    errors_encountered: int = 0

    def reset(self) -> None:
        """Reset all statistics to zero."""
        self.total_files_scanned = 0
        self.total_games_found = 0
        self.duplicates_found = 0
        self.files_processed = 0
        self.files_moved = 0
        self.files_deleted = 0
        self.errors_encountered = 0


__all__ = [
    "CleanupConfig",
    "ProcessingStats",
]
