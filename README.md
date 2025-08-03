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

1. **Register a Twitch developer application**
   - Visit the [Twitch Developers console](https://dev.twitch.tv/console)
   - Sign in and create a new application to obtain your **Client ID** and **Client Secret**
   - Follow the [IGDB Getting Started guide](https://api-docs.igdb.com/#getting-started) for detailed instructions
2. **Request an access token** using your credentials:
   ```bash
   curl -X POST https://id.twitch.tv/oauth2/token \
        -d 'client_id=YOUR_CLIENT_ID' \
        -d 'client_secret=YOUR_CLIENT_SECRET' \
        -d 'grant_type=client_credentials'
   ```
   The response includes an `access_token` value.
3. **Export your credentials** so the tool can access the IGDB API:
   - **Unix/macOS**
     ```bash
     export IGDB_CLIENT_ID="YOUR_CLIENT_ID"
     export IGDB_ACCESS_TOKEN="YOUR_ACCESS_TOKEN"
     ```
   - **Windows PowerShell**
     ```powershell
     setx IGDB_CLIENT_ID "YOUR_CLIENT_ID"
     setx IGDB_ACCESS_TOKEN "YOUR_ACCESS_TOKEN"
     # For the current session only:
     $env:IGDB_CLIENT_ID="YOUR_CLIENT_ID"
     $env:IGDB_ACCESS_TOKEN="YOUR_ACCESS_TOKEN"
     ```
4. Run the tool. If these variables are not set, the tool still operates
   but falls back to filename matching, which may reduce accuracy.
