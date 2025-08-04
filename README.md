# ROM Collection Cleanup Tool

A Python utility to streamline large ROM collections by removing redundant regional duplicates. It scans a directory of ROM files and removes or relocates Japanese versions when a corresponding USA release exists, while keeping games that are only available in Japanese. Optional integration with IGDB allows fuzzy name matching.

## Features
- Detect Japanese ROMs that have US equivalents and remove or move them.
- Supports many ROM file extensions (zip, nes, snes, gb, gba, nds, etc.).
- Optional IGDB lookup for alternative names and platform awareness.
- Preview mode (`--dry-run`) shows actions without modifying files.
- Choose to delete or move unwanted files to a `to_delete` subfolder.
- Basic GUI available via `rom_cleanup_gui.py` for interactive use.

## Installation

### Option 1: Using pip (Recommended)
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

### IGDB API Setup (Optional)

Some features, such as alternative name lookup, rely on the IGDB API. **For security reasons, you must provide your own credentials** - no default credentials are included in the codebase.

#### **Easy Setup with Token Generator**

The easiest way to get IGDB credentials is using the included token generator:

```bash
python get_igdb_token.py
```

This script will:
- Guide you through entering your IGDB Client ID and Client Secret
- Automatically get a valid access token using Twitch's OAuth2 flow
- Test the connection to ensure everything works
- Show you exactly how to use the credentials with the ROM cleanup tool

#### **Manual Setup**

You can also provide credentials either via environment variables or through the GUI's **Advanced** tab. See [README_API_CREDENTIALS.md](README_API_CREDENTIALS.md) for a step-by-step guide to obtaining these values.

```bash
export IGDB_CLIENT_ID="your-client-id"
export IGDB_ACCESS_TOKEN="your-access-token"
```

If credentials are not supplied, the program will use basic name matching only and skip IGDB lookups. This is perfectly functional for most use cases.

## IGDB API Limits & Usage Guidelines

When using IGDB integration, be aware of the following API constraints:

### **Rate Limits**
- **Maximum Rate**: 4 requests per second per API key
- **Recommended Rate**: 3 requests per second (0.33s delay) for safety margin
- **Daily Limit**: 10,000 requests per day per API key
- **Request Timeout**: 30 seconds per request

### **Best Practices**
- **Caching**: The tool automatically caches IGDB results to minimize API usage
- **Progress Indicators**: Large collections show progress to track API usage
- **Error Handling**: Implements exponential backoff for rate limit errors (HTTP 429)
- **Conservative Delays**: Uses 0.25s delays between requests by default

### **Estimation for Large Collections**
- **Small collection** (100-500 ROMs): ~2-8 minutes of API calls
- **Medium collection** (500-2000 ROMs): ~8-33 minutes of API calls  
- **Large collection** (2000+ ROMs): Plan for 1+ hours, consider running overnight

The tool processes ROMs efficiently by grouping similar names and using intelligent caching to avoid duplicate API calls for the same game.

## Security & Privacy

- **No hardcoded credentials**: The tool requires you to provide your own IGDB API credentials
- **Local processing**: All ROM analysis happens locally on your machine
- **Optional cloud features**: IGDB integration is optional and can be disabled
- **Data safety**: The tool includes dry-run mode and move-to-folder options for safe testing
