"""
Configuration and statistics dataclasses for ROM cleanup tool.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class CleanupConfig:
    """Configuration for ROM cleanup operations."""

    # Directory settings
    rom_directory: Path
    dry_run: bool = False
    move_to_folder: bool = False

    # File processing settings
    rom_extensions: Set[str] = field(default_factory=set)
    custom_extensions: Optional[str] = None

    # API settings
    use_igdb_api: bool = True
    use_thegamesdb_api: bool = False
    igdb_client_id: Optional[str] = None
    igdb_access_token: Optional[str] = None
    thegamesdb_api_key: Optional[str] = None

    # Processing settings
    preferred_region: str = "usa"
    keep_japanese_only: bool = True
    enable_cross_language_matching: bool = True

    # Logging settings
    verbose: bool = False
    quiet: bool = False
    log_to_file: bool = False
    log_file: Optional[Path] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.rom_directory.exists():
            raise FileNotFoundError(
                f"ROM directory does not exist: {self.rom_directory}"
            )

        if not self.rom_directory.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self.rom_directory}")

        if self.verbose and self.quiet:
            raise ValueError("Cannot use both --verbose and --quiet")

        if self.dry_run and self.move_to_folder:
            # This is actually valid - dry run with move to folder shows what would be moved
            pass


@dataclass
class ProcessingStats:
    """Statistics for ROM processing operations."""

    # File counts
    total_files_scanned: int = 0
    total_games_found: int = 0
    files_to_remove: int = 0
    files_removed: int = 0
    files_moved: int = 0

    # Processing details
    multi_disc_games: int = 0
    cross_regional_duplicates: int = 0
    same_region_duplicates: int = 0

    # API usage
    api_queries_made: int = 0
    api_cache_hits: int = 0
    cross_language_matches: int = 0

    # Timing
    scan_time_seconds: float = 0.0
    processing_time_seconds: float = 0.0
    total_time_seconds: float = 0.0

    # Errors
    errors_encountered: int = 0
    permission_errors: int = 0
    file_not_found_errors: int = 0

    def __post_init__(self):
        """Calculate total time if individual times are set."""
        if self.scan_time_seconds > 0 and self.processing_time_seconds > 0:
            self.total_time_seconds = (
                self.scan_time_seconds + self.processing_time_seconds
            )

    def add_error(self, error_type: str = "general"):
        """Increment error counters."""
        self.errors_encountered += 1
        if error_type == "permission":
            self.permission_errors += 1
        elif error_type == "file_not_found":
            self.file_not_found_errors += 1

    def get_summary(self) -> Dict[str, any]:
        """Get a summary dictionary of the statistics."""
        return {
            "total_files_scanned": self.total_files_scanned,
            "total_games_found": self.total_games_found,
            "files_to_remove": self.files_to_remove,
            "files_removed": self.files_removed,
            "files_moved": self.files_moved,
            "multi_disc_games": self.multi_disc_games,
            "cross_regional_duplicates": self.cross_regional_duplicates,
            "same_region_duplicates": self.same_region_duplicates,
            "api_queries_made": self.api_queries_made,
            "api_cache_hits": self.api_cache_hits,
            "cross_language_matches": self.cross_language_matches,
            "total_time_seconds": self.total_time_seconds,
            "errors_encountered": self.errors_encountered,
        }

    def __str__(self) -> str:
        """String representation of processing statistics."""
        summary = self.get_summary()
        return (
            f"Processing Summary:\n"
            f"  Files scanned: {summary['total_files_scanned']}\n"
            f"  Games found: {summary['total_games_found']}\n"
            f"  Files to remove: {summary['files_to_remove']}\n"
            f"  Files removed: {summary['files_removed']}\n"
            f"  Files moved: {summary['files_moved']}\n"
            f"  Multi-disc games: {summary['multi_disc_games']}\n"
            f"  Cross-regional duplicates: {summary['cross_regional_duplicates']}\n"
            f"  Same-region duplicates: {summary['same_region_duplicates']}\n"
            f"  API queries: {summary['api_queries_made']}\n"
            f"  Cache hits: {summary['api_cache_hits']}\n"
            f"  Cross-language matches: {summary['cross_language_matches']}\n"
            f"  Total time: {summary['total_time_seconds']:.2f}s\n"
            f"  Errors: {summary['errors_encountered']}"
        )
