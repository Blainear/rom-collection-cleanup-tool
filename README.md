# ROM Collection Cleanup Tool

A Python utility to streamline large ROM collections by removing redundant regional duplicates. It scans a directory of ROM files and removes or relocates Japanese versions when a corresponding USA release exists, while keeping games that are only available in Japanese. Optional integration with TheGamesDB provides enhanced cross-language ROM matching specifically designed for ROM collectors.

## Features
- Detect Japanese ROMs that have US equivalents and remove or move them.
- Supports many ROM file extensions (zip, nes, snes, gb, gba, nds, etc.).
- Optional TheGamesDB lookup for enhanced cross-language ROM matching.
- Beautiful dark mode GUI with professional styling and better organization.
- Preview mode (`--dry-run`) shows actions without modifying files.
- Choose to delete or move unwanted files to a `to_delete` subfolder.
- Modern GUI available via `rom_cleanup_gui.py` with intuitive interface.

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

3. (Optional) Install build dependencies if you plan to create a standalone executable:

```bash
pip install -r requirements-build.txt
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

### Building an Executable

To create a standalone executable of the GUI, the project provides `build_exe.py`. The script uses [PyInstaller](https://www.pyinstaller.org/), which must be installed manually:

```bash
pip install pyinstaller
python build_exe.py
```

The resulting executable will be placed in the `dist/` directory.

### TheGamesDB API Setup (Optional)

Enhanced cross-language ROM matching is powered by TheGamesDB, a database specifically designed for ROM collectors and emulation enthusiasts. **You need to provide your own API key** - no credentials are included for security reasons.

#### **Getting Your API Key**

1. **Visit TheGamesDB**: Go to [https://thegamesdb.net/](https://thegamesdb.net/)
2. **Join Discord**: Click the Discord link on their website
3. **Request Access**: Ask for API access in their Discord channel
4. **Get Your Key**: Once approved, you'll receive your API key
5. **Configure**: Enter the key in the GUI's Advanced Settings tab

#### **Using Your API Key**

You can provide your API key through the GUI's **Advanced Settings** tab, which includes:
- Simple API key input field
- Connection testing functionality
- Automatic credential saving
- Clear setup instructions

If no API key is provided, the program will use basic filename matching only, which works well for most collections.

## TheGamesDB API Benefits

TheGamesDB offers several advantages for ROM collections:

### **ROM-Focused Design**
- **Database built for emulation**: Designed specifically for ROM collectors
- **Better cross-language matching**: Superior handling of regional game variants
- **Comprehensive ROM data**: Extensive coverage of retro gaming platforms

### **Enhanced Matching**
- **Cross-language detection**: Matches games like "Biohazard" (Japan) with "Resident Evil" (USA)
- **Regional variants**: Identifies "Street Fighter Zero" (Japan) as "Street Fighter Alpha" (USA)
- **Platform awareness**: Better matching based on file extensions and platforms

### **User-Friendly**
- **Single API key**: Simpler setup compared to client ID/secret systems
- **Reasonable limits**: Designed for community use with fair rate limiting
- **Free access**: No cost for reasonable usage by ROM collectors

The tool automatically caches TheGamesDB results to minimize API usage and includes intelligent retry logic for reliable operation.

## Security & Privacy

- **No hardcoded credentials**: The tool requires you to provide your own TheGamesDB API key
- **Local processing**: All ROM analysis happens locally on your machine
- **Optional cloud features**: TheGamesDB integration is optional and can be disabled
- **Data safety**: The tool includes dry-run mode and move-to-folder options for safe testing
- **Credential storage**: API keys are stored locally in encrypted JSON format
