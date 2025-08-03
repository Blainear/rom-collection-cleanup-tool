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

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Contributing

Contributions are welcome! Feel free to open an issue for bug reports or feature requests, or submit a pull request with improvements.

