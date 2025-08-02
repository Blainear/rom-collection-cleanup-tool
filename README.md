# ROM Cleanup Tool

A Python-based tool for automatically identifying and removing duplicate ROM files while preserving the highest quality versions.

## Features

- **Smart Duplicate Detection**: Identifies duplicates based on game titles, not just filenames
- **Regional Preference**: Keeps USA versions over Japanese/European duplicates
- **Game Database Integration**: Optional IGDB API for accurate regional variant matching
- **Safety Features**: Dry-run mode and move-to-folder option for safe operation
- **Wide Format Support**: Supports 25+ ROM file formats
- **GUI Available**: Both command-line and graphical user interface

## Supported Formats

NES, SNES, N64, GameBoy, GBA, GameCube, Genesis, ISO, and many more including:
`.nes`, `.snes`, `.n64`, `.gb`, `.gba`, `.gcm`, `.gen`, `.iso`, `.zip`, `.7z`

## Quick Start

### Command Line
```bash
# Dry run (safe preview)
python rom_cleanup.py /path/to/roms --dry-run

# Move duplicates to folder for review
python rom_cleanup.py /path/to/roms --move-to-folder

# Actually delete duplicates (use with caution)
python rom_cleanup.py /path/to/roms
```

### GUI Version
```bash
python rom_cleanup_gui.py
```

### Standalone Executable
Run `ROM_Cleanup_Tool.exe` - no Python installation required.

## How It Works

1. Scans your ROM directory for supported file formats
2. Extracts game names and regions from filenames
3. Uses IGDB game database to match regional variants
4. Groups duplicates and keeps the best version (USA > Europe > Japan)
5. Safely removes or moves lower-priority duplicates

## Safety Levels

1. **`--dry-run`**: Preview what would be deleted (recommended first step)
2. **`--move-to-folder`**: Move duplicates to `to_delete` folder for review
3. **Direct deletion**: Permanently removes duplicates (use with caution)

## Requirements

- Python 3.7+
- `requests` library (for optional IGDB API)

## Optional: IGDB API Setup

For enhanced regional variant matching, you can optionally set up IGDB API:

1. Create a free account at [Twitch Developer Console](https://dev.twitch.tv/console)
2. Create a new application with these settings:
   - Name: ROM Cleanup Tool
   - OAuth Redirect URLs: `https://localhost`
   - Category: Application Integration
3. Set environment variables:
   ```bash
   set IGDB_CLIENT_ID=your_client_id_here
   set IGDB_ACCESS_TOKEN=your_access_token_here
   ```

**Note**: The tool works without API credentials using basic filename matching.

## Installation

```bash
pip install -r requirements.txt
```

## License

MIT License - see LICENSE file for details.