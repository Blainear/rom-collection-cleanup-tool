# ROM Collection Cleanup Tool v1.0.0

## 🎮 **Pre-built Windows Executable**

Download `ROM_Cleanup_Tool.exe` - No Python installation required!

## ✨ **Features**

- **Smart Duplicate Detection**: Identifies duplicates based on game titles, not just filenames
- **Regional Preference**: Automatically keeps USA versions over Japanese/European duplicates  
- **Game Database Integration**: Optional IGDB API for enhanced regional variant matching
- **Safety First**: Multiple safety levels (dry-run, move-to-folder, direct deletion)
- **Wide Format Support**: 25+ ROM file formats including NES, SNES, N64, GameBoy, GameCube, Genesis, PS2
- **User-Friendly GUI**: Easy-to-use graphical interface with progress tracking
- **Professional Features**: Backup options, custom extensions, subdirectory preservation

## 🚀 **Quick Start**

1. **Download** `ROM_Cleanup_Tool.exe`
2. **Run** the executable (Windows may show a security warning - click "More info" → "Run anyway")
3. **Select** your ROM directory
4. **Choose** safety level (recommend "Move to Folder" for first use)
5. **Review** results before final deletion

## 🔧 **Optional: Enhanced Matching**

For improved regional variant detection, set up IGDB API:

1. Create account at [Twitch Developer Console](https://dev.twitch.tv/console)
2. Create application with redirect URL: `https://localhost`
3. Set environment variables:
   ```
   IGDB_CLIENT_ID=your_client_id
   IGDB_ACCESS_TOKEN=your_access_token
   ```

**Note**: Tool works great without API using smart filename matching!

## 📋 **System Requirements**

- Windows 10/11
- No additional software required
- ~11MB disk space

## 🛡️ **Safety Features**

- **Dry Run**: Preview changes without modification
- **Move to Folder**: Safe review before deletion  
- **Backup Options**: Optional backup creation
- **Progress Tracking**: Real-time scan progress
- **Detailed Logging**: Complete operation history

## 🎯 **Perfect For**

- ROM collectors with duplicate releases
- Retro gaming enthusiasts
- Anyone wanting to organize ROM collections
- Users who prefer USA releases over regional variants

---

**Made with ❤️ for the retro gaming community**