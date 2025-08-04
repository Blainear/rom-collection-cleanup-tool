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

### IGDB API Setup (Optional)

Some features, such as alternative name lookup, rely on the IGDB API. **For security reasons, you must provide your own credentials** - no default credentials are included in the codebase.

You can provide credentials either via environment variables or through the GUI's **Advanced** tab. See [README_API_CREDENTIALS.md](README_API_CREDENTIALS.md) for a step-by-step guide to obtaining these values.

```bash
export IGDB_CLIENT_ID="your-client-id"
export IGDB_ACCESS_TOKEN="your-access-token"
```

If credentials are not supplied, the program will use basic name matching only and skip IGDB lookups. This is perfectly functional for most use cases.

## Security & Privacy

- **No hardcoded credentials**: The tool requires you to provide your own IGDB API credentials
- **Local processing**: All ROM analysis happens locally on your machine
- **Optional cloud features**: IGDB integration is optional and can be disabled
- **Data safety**: The tool includes dry-run mode and move-to-folder options for safe testing
