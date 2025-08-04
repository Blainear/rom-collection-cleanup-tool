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

The IGDB integration provides enhanced ROM matching capabilities. To set it up:

#### 1. Create a Twitch Developer Application
1. Go to [Twitch Developer Console](https://dev.twitch.tv/console)
2. Log in with your Twitch account (create one if needed)
3. Click "Create App"
4. Fill in the required fields:
   - **Name**: Choose any name for your application
   - **OAuth Redirect URLs**: `http://localhost` (required but not used)
   - **Category**: Select "Application Integration"
5. Click "Create"
6. Note down your **Client ID** from the app details

#### 2. Generate Client Secret
1. In your app details, click "New Secret"
2. Copy the generated **Client Secret** immediately (it won't be shown again)

#### 3. Configure Credentials
Create a `config.json` file in the project root directory with your credentials:
```json
{
  "igdb_client_id": "your_client_id_here",
  "igdb_client_secret": "your_client_secret_here"
}
```

**Security Note:** Never commit `config.json` to version control. The file is already included in `.gitignore`.

#### 4. Troubleshooting

**Invalid Credentials Error:**
- Verify your Client ID and Client Secret are correct
- Ensure there are no extra spaces or characters in `config.json`
- Try generating a new Client Secret if the current one isn't working

**API Rate Limiting:**
- IGDB has rate limits; the tool includes automatic retry logic
- If you encounter persistent rate limit errors, wait a few minutes before retrying

**Network/Connection Issues:**
- Ensure you have an active internet connection
- Check if your firewall or proxy is blocking requests to `api.igdb.com`

**Token Refresh:**
- Access tokens are automatically managed and refreshed as needed
- If you see authentication errors, delete any cached token files and restart the application

## License
This project is released under the MIT License. See the LICENSE file for details.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
