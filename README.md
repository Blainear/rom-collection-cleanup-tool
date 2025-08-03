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

Some features, such as alternative name lookup, rely on the IGDB API. To
enable them, create an API application at [IGDB](https://api-docs.igdb.com/)
and export your credentials before running the tool:

```bash
export IGDB_CLIENT_ID="your-client-id"
export IGDB_ACCESS_TOKEN="your-access-token"
```

If these variables are not set, the program will skip IGDB lookups.
