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
2. Install dependencies:

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

Providing IGDB credentials improves matching, particularly for games with alternate titles.

1. [Create a Twitch developer application](https://dev.twitch.tv/console) to obtain a **Client ID** and **Client Secret**.
2. Request an access token:

```bash
curl -X POST https://id.twitch.tv/oauth2/token \
  -d 'client_id=YOUR_CLIENT_ID' \
  -d 'client_secret=YOUR_CLIENT_SECRET' \
  -d 'grant_type=client_credentials'
```

3. Export the credentials:

```bash
export IGDB_CLIENT_ID=YOUR_CLIENT_ID
export IGDB_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
```

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Contributing
Contributions are welcome! Open an issue for bugs or feature requests, or submit a pull request.

