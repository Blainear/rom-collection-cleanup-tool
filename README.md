# ROM Collection Cleanup Tool
A user-friendly GUI tool for managing ROM collections by removing duplicates based on region preferences while preserving unique releases.

## Features

### Core Functionality
- **Smart Duplicate Detection**: Identifies games with multiple regional variants
- **Region Priority**: Choose preferred regions (USA, Europe, Japan, World)
- **Safe Operations**: Move, delete, or backup duplicates with safety options
- **Subdirectory Preservation**: Maintains folder structure during operations
- **Comprehensive Format Support**: Supports all major ROM formats

### Enhanced Features (v2.0)
- **Startup API Check**: Automatic IGDB API connection testing on startup
- **Manual API Testing**: "Check API" button for troubleshooting
- **Process Control**: "Stop Process" button to safely stop operations
- **Improved Region Detection**: Enhanced pattern matching for better accuracy
- **Real-time Logging**: Detailed progress updates with timestamps
- **Thread-safe Operations**: Background processing with UI responsiveness

### IGDB Integration
- **Enhanced Game Matching**: Uses IGDB API for better game name matching
- **Alternative Names**: Handles different naming conventions and translations
- **Platform-specific Queries**: Optimized searches based on file extensions
- **Caching System**: Efficient API usage with local caching

## Quick Start

### Prerequisites
- Python 3.7+
- Required packages: `tkinter`, `requests` (see requirements.txt)

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up IGDB API credentials (optional but recommended)

### IGDB API Setup (Optional)

## Usage

### Command-Line Interface (CLI)

Invoke the script with the target directory:

```bash
python rom_cleanup.py /path/to/roms
```

Preview actions without modifying files:

```bash
python rom_cleanup.py /path/to/roms --dry-run
```

Move duplicates to a review folder instead of deleting:

```bash
python rom_cleanup.py /path/to/roms --move-to-folder
```

Include additional file extensions:

```bash
python rom_cleanup.py /path/to/roms --extensions 7z,zip
```

### Graphical User Interface (GUI)

Launch the GUI with:

```bash
python rom_cleanup_gui.py
```

The interface performs a startup IGDB API check and includes a **Check API** button for manual testing. During scanning or cleanup operations, use the **Stop Process** button to halt processing safely.

