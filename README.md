# ROM Collection Cleanup Tool

A user-friendly GUI tool for managing ROM collections by removing duplicates based on region preferences while preserving unique releases.

## ✨ Features

### 🎯 Core Functionality
- **Smart Duplicate Detection**: Identifies games with multiple regional variants
- **Region Priority**: Choose preferred regions (USA, Europe, Japan, World)
- **Safe Operations**: Move, delete, or backup duplicates with safety options
- **Subdirectory Preservation**: Maintains folder structure during operations
- **Comprehensive Format Support**: Supports all major ROM formats

### 🔧 Enhanced Features (v2.0)
- **Startup API Check**: Automatic IGDB API connection testing on startup
- **Manual API Testing**: "Check API" button for troubleshooting
- **Process Control**: "Stop Process" button to safely stop operations
- **Improved Region Detection**: Enhanced pattern matching for better accuracy
- **Real-time Logging**: Detailed progress updates with timestamps
- **Thread-safe Operations**: Background processing with UI responsiveness

### 🌐 IGDB Integration
- **Enhanced Game Matching**: Uses IGDB API for better game name matching
- **Alternative Names**: Handles different naming conventions and translations
- **Platform-specific Queries**: Optimized searches based on file extensions
- **Caching System**: Efficient API usage with local caching

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Required packages: `tkinter`, `requests` (see requirements.txt)

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up IGDB API credentials (optional but recommended)

### IGDB API Setup (Optional)
1. Create an account at [IGDB](https://api.igdb.com/)
2. Set environment variables:
   ```bash
   export IGDB_CLIENT_ID="your_client_id"
   export IGDB_ACCESS_TOKEN="your_access_token"
   ```

### Usage
1. Run the application: `python rom_cleanup_gui.py`
2. Select your ROM directory
3. Configure preferences (region priority, operation mode)
4. Click "Scan ROMs" to analyze your collection
5. Use "Preview Changes" to see what would be processed
6. Click "Execute" to perform the cleanup

## 🎮 Supported Formats

### Nintendo
- **NES**: `.nes`
- **SNES**: `.snes`, `.smc`, `.sfc`
- **Game Boy**: `.gb`, `.gbc`, `.gba`
- **Nintendo DS**: `.nds`
- **Nintendo 64**: `.n64`, `.z64`, `.v64`
- **GameCube**: `.gcm`, `.gcz`, `.ciso`
- **Wii**: `.wbfs`, `.rvz`

### Sega
- **Mega Drive/Genesis**: `.md`, `.gen`, `.smd`

### Sony
- **PlayStation**: `.iso`, `.bin`, `.cue`, `.chd`
- **PlayStation 2**: `.iso`, `.mdf`, `.nrg`
- **PSP**: `.pbp`, `.cso`

### Archives
- **Compressed**: `.zip`, `.7z`, `.rar`

## ⚙️ Configuration

### Operation Modes
- **Move**: Safely move duplicates to `to_delete` folder
- **Delete**: Permanently remove duplicates
- **Backup**: Create backup before deletion

### Region Priority
- **USA**: Prefer USA releases
- **Europe**: Prefer European releases  
- **Japan**: Prefer Japanese releases
- **World**: Prefer World/International releases

### Preservation Options
- **Keep Japanese-only**: Preserve Japan-exclusive releases
- **Keep Europe-only**: Preserve Europe-exclusive releases
- **Preserve Subdirectories**: Maintain folder structure

## 🔧 Advanced Features

### API Connection Management
- **Startup Check**: Automatic API connectivity test
- **Manual Testing**: Force API connection check
- **Status Indicators**: Clear ✅/❌ feedback
- **Error Handling**: Detailed error messages

### Process Control
- **Safe Stopping**: Stop operations without data loss
- **Progress Preservation**: Maintain partial progress
- **Thread Management**: Responsive UI during operations
- **Status Updates**: Real-time operation feedback

### Enhanced Logging
- **Timestamped Messages**: All actions logged with time
- **Progress Tracking**: Real-time operation progress
- **Error Reporting**: Detailed error information
- **Console Integration**: Redirects console output to GUI

## 📋 Usage Examples

### Basic Cleanup
1. Select ROM directory
2. Choose "USA" as preferred region
3. Select "Move" operation mode
4. Scan and preview changes
5. Execute cleanup

### Advanced Configuration
1. Set custom file extensions if needed
2. Configure preservation options
3. Use "Check API" to verify connectivity
4. Monitor progress in real-time
5. Stop operations if needed

## 🛡️ Safety Features

- **Preview Mode**: See exactly what will be processed
- **Safe Operations**: Move to temporary folder by default
- **Backup Options**: Create backups before deletion
- **Process Control**: Stop operations at any time
- **Error Recovery**: Graceful handling of file operations

## 🔍 Troubleshooting

### API Issues
- Use "Check API" button to test connectivity
- Verify environment variables are set correctly
- Check network connection and firewall settings

### Process Issues
- Use "Stop Process" to safely halt operations
- Check log messages for detailed error information
- Verify file permissions and disk space

### Region Detection
- Check log for region detection results
- Verify filename patterns match expected format
- Use custom extensions if needed

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub.