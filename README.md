# ROM Collection Cleanup Tool

A Python utility to streamline large ROM collections by removing redundant regional duplicates. It scans a directory of ROM files and removes or relocates Japanese versions when a corresponding USA release exists, while keeping games that are only available in Japanese. **Enhanced with built-in TheGamesDB integration, progressive search algorithm, and intelligent rate limiting for reliable operation.**

## Features
- **🎯 Progressive Search Algorithm**: Advanced matching that tries multiple search terms for games with subtitles, editions, and special releases
- **⚡ Built-in API Integration**: TheGamesDB support with default public key - works immediately out-of-the-box
- **🛡️ Intelligent Rate Limiting**: Automatic API throttling prevents 403/429 errors and ensures reliable operation
- **🎮 Superior Game Matching**: Finds matches for complex names like "Baroque - Yuganda Mousou (English)" → "Baroque"
- **🎨 Enhanced User Interface**: Fixed readability issues, detailed progress feedback, and professional dark mode styling
- Detect Japanese ROMs that have US equivalents and remove or move them
- Supports many ROM file extensions (zip, nes, snes, gb, gba, nds, etc.)
- Preview mode (`--dry-run`) shows actions without modifying files
- Choose to delete or move unwanted files to a `to_delete` subfolder
- Modern GUI with intuitive interface and real-time progress updates

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

3. (Recommended) Install security dependencies for enhanced credential protection:

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

### Building an Executable

To create a standalone executable of the GUI, the project provides `build_exe.py`. The script uses [PyInstaller](https://www.pyinstaller.org/), which must be installed manually:

## Getting Started

**The tool works excellently out-of-the-box** using intelligent filename analysis to detect regional duplicates. Most ROM collections will be cleaned effectively without any additional setup.

**For enhanced cross-regional matching** (like detecting that "Biohazard" = "Resident Evil"), you can optionally configure API access to external game databases:

The tool supports two database options for enhanced cross-language ROM matching. Choose the one that works best for you:

#### **Option 1: TheGamesDB (Recommended for ROM collectors)**
ROM-focused database with excellent cross-language matching, but requires Discord access to get an API key.

#### **Option 2: IGDB (No Discord required)**
Comprehensive game database with detailed metadata. Easier to obtain credentials via Twitch Developer Console.

#### **Setup Instructions**

**For TheGamesDB:**
1. Visit [https://thegamesdb.net/](https://thegamesdb.net/)
2. Join their Discord server (link on the website)
3. Request API access in their Discord channel
4. Once approved, you'll receive your API key
5. Enter the key in the GUI's Advanced Settings tab

**For IGDB:**
1. Click **"Generate IGDB Token"** in the Advanced Settings tab
2. Enter your Client ID and Client Secret in the integrated token generator
3. The tool will automatically fill in your credentials after successful generation
4. Alternative: Manually get credentials from [Twitch Developer Console](https://dev.twitch.tv/console/apps)

#### **Using the APIs**

The GUI's **Advanced Settings** tab provides:
- **Database Selection**: Choose between TheGamesDB and IGDB
- **Credential Input**: Enter your API key or Client ID/Token
- **Connection Testing**: Verify your credentials work
- **Automatic Saving**: Credentials are saved locally and encrypted
- **Integrated Token Generator**: Built-in IGDB token generator with auto-credential filling

**With the built-in API integration**, the program provides enhanced cross-regional matching automatically. **Without API configuration**, the program falls back to intelligent filename analysis which works excellently for most ROM collections.

## Database Comparison

### **TheGamesDB Benefits**
- **ROM-Focused**: Built specifically for ROM collectors and emulation
- **Cross-Language Matching**: Excellent handling of regional variants (Biohazard ↔ Resident Evil)
- **Community-Driven**: Free access with reasonable rate limits
- **Simple Setup**: Single API key (once you get Discord access)

### **IGDB Benefits**
- **No Discord Required**: Get credentials directly from Twitch Developer Console
- **Comprehensive Data**: Detailed game metadata and extensive database
- **Easy Token Generation**: Integrated token generator with automatic credential filling
- **Established API**: Well-documented with good reliability

### **Enhanced Matching Examples**
Both APIs help identify cross-regional duplicates:
- **"Biohazard" (Japan) ↔ "Resident Evil" (USA)**
- **"Street Fighter Zero" (Japan) ↔ "Street Fighter Alpha" (USA)**
- **"Rockman" (Japan) ↔ "Mega Man" (USA)**

The tool automatically caches API results to minimize usage and includes intelligent retry logic for reliable operation.

## Security & Privacy

- **Secure credential storage**: Uses system keyring with encrypted fallback storage
- **No hardcoded credentials**: The tool requires you to provide your own API keys
- **Local processing**: All ROM analysis happens locally on your machine
- **Optional cloud features**: TheGamesDB integration is optional and can be disabled
- **Data safety**: The tool includes dry-run mode and move-to-folder options for safe testing
- **Enhanced security**: Install with `pip install -e ".[security]"` for maximum protection

For detailed security information, see [SECURITY.md](SECURITY.md).


