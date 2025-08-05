# ROM Collection Cleanup Tool

A Python utility that streamlines large ROM collections by removing redundant regional duplicates. It scans a directory of ROM files and removes or relocates Japanese versions when a corresponding USA release exists, while keeping games that are only available in Japanese. The tool includes TheGamesDB integration, a progressive search algorithm, and rate limiting for reliable operation.

## Features
- Progressive search algorithm that tries multiple search terms for games with subtitles, editions, and special releases
- Built-in API integration with a default TheGamesDB public key
- Intelligent rate limiting to avoid API throttling
- Game matching capable of handling complex names such as "Baroque - Yuganda Mousou (English)" → "Baroque"
- Improved user interface with readability fixes, progress feedback, and dark mode styling
- Detects Japanese ROMs that have US equivalents and removes or moves them
- Supports many ROM file extensions (zip, nes, snes, gb, gba, nds, etc.)
- Preview mode (`--dry-run`) shows actions without modifying files
- Option to delete or move unwanted files to a `to_delete` subfolder
- Graphical interface with real-time progress updates

## Installation

### Option 1: pip installation
```bash
# Install from the project directory
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Option 2: Manual installation
1. Ensure Python 3.9+ is installed.
2. Install runtime dependencies:

```bash
pip install -r requirements.txt
```

3. Install security dependencies for enhanced credential protection:

## Usage

### Command line

```bash
python rom_cleanup.py /path/to/roms --dry-run --move-to-folder
```

- `--dry-run` – list actions without deleting or moving files.
- `--move-to-folder` – move duplicates into a `to_delete` folder instead of deleting.

### GUI

```bash
python rom_cleanup_gui.py
```

The GUI provides directory selection and toggle options for the same features as the CLI.

### Building an executable

To create a standalone executable of the GUI, the project provides `build_exe.py`. The script uses [PyInstaller](https://www.pyinstaller.org/), which must be installed manually.

## Getting started

The tool can operate without additional configuration by using filename analysis to detect regional duplicates.

For improved cross-regional matching, API access to external game databases can be configured. The tool supports two options:

#### Option 1: TheGamesDB
Database focused on ROM collections with strong cross-language matching. Discord access is required to obtain an API key.

#### Option 2: IGDB
Comprehensive game database accessible through credentials from the Twitch Developer Console.

#### Setup instructions

**TheGamesDB**
1. Visit [https://thegamesdb.net/](https://thegamesdb.net/).
2. Join the Discord server linked on the site.
3. Request API access in their Discord channel.
4. Enter the API key in the GUI's Advanced Settings tab.

**IGDB**
1. Click "Generate IGDB Token" in the Advanced Settings tab.
2. Enter your Client ID and Client Secret in the token generator.
3. Alternatively, obtain credentials from the [Twitch Developer Console](https://dev.twitch.tv/console/apps) and enter them manually.

#### Using the APIs

The GUI's Advanced Settings tab provides:
- Database selection between TheGamesDB and IGDB
- Credential input for an API key or Client ID and token
- Connection testing for credential validation
- Local encrypted storage of credentials
- An IGDB token generator

With API integration enabled, the program provides enhanced cross-regional matching. Without configuration, it defaults to filename analysis, which is sufficient for many collections.

## Database comparison

### TheGamesDB features
- Designed for ROM collectors and emulation
- Handles regional variants effectively (e.g., Biohazard ↔ Resident Evil)
- Free access with reasonable rate limits
- Requires a single API key obtained via Discord

### IGDB features
- Credentials available directly from the Twitch Developer Console
- Provides extensive metadata
- Includes an integrated token generator
- Well-documented and reliable

### Enhanced matching examples
Both APIs help identify cross-regional duplicates:
- "Biohazard" (Japan) ↔ "Resident Evil" (USA)
- "Street Fighter Zero" (Japan) ↔ "Street Fighter Alpha" (USA)
- "Rockman" (Japan) ↔ "Mega Man" (USA)

The tool caches API results to minimize usage and includes retry logic for reliable operation.

## Security and privacy

- Secure credential storage using the system keyring with encrypted fallback storage
- No hardcoded credentials; users must provide their own API keys
- All ROM analysis occurs locally
- TheGamesDB integration is optional and can be disabled
- Dry-run mode and move-to-folder options support safe testing
- Install with `pip install -e ".[security]"` for additional security features

For detailed security information, see [SECURITY.md](SECURITY.md).


