"""
Configuration classes for ROM cleanup tool.

This module provides structured configuration classes for better
organization of settings and parameters.
"""

from dataclasses import dataclass
from typing import Set, Optional
from pathlib import Path


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
        """Get the set of ROM file extensions to process."""
        default_extensions = {
            # Archive formats
            '.zip', '.7z', '.rar',
            # Nintendo systems
            '.nes', '.snes', '.smc', '.sfc', '.gb', '.gbc', '.gba', '.nds', '.3ds', '.cia',
            '.n64', '.z64', '.v64', '.ndd', '.gcm', '.gcz', '.rvz', '.wbfs', '.xci', '.nsp',
            '.vb', '.lnx', '.ngp', '.ngc',
            # Sega systems  
            '.md', '.gen', '.smd', '.gg', '.sms', '.32x', '.sat', '.gdi',
            # Sony systems
            '.bin', '.iso', '.cue', '.chd', '.pbp', '.cso', '.ciso',
            # PC Engine/TurboGrafx
            '.pce', '.sgx',
            # Atari systems
            '.a26', '.a78', '.st', '.d64',
            # Other retro systems
            '.col', '.int', '.vec', '.ws', '.wsc',
            # Disk images
            '.img', '.ima', '.dsk', '.adf', '.mdf', '.nrg',
            # Tape formats
            '.tap', '.tzx',
            # Spectrum formats
            '.sna', '.z80'
        }
        
        if self.custom_extensions:
            custom_exts = set()
            for ext in self.custom_extensions.split(','):
                ext = ext.strip().lower()
                ext = ext if ext.startswith('.') else '.' + ext
                custom_exts.add(ext)
            default_extensions.update(custom_exts)
        
        return default_extensions
    
    def validate(self) -> bool:
        """Validate the configuration settings."""
        if not self.rom_directory:
            return False
        
        if not Path(self.rom_directory).exists():
            return False
        
        if self.operation_mode not in ['move', 'delete', 'backup']:
            return False
        
        if self.region_priority not in ['usa', 'europe', 'japan', 'world']:
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