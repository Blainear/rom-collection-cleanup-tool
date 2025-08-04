# ROM Cleanup Tool - Comprehensive Test Setup

This directory contains a comprehensive test setup for the ROM cleanup tool with dummy ROMs that test all features of the cleanup and scan functionality.

## Test Directory Structure

```
test_roms_comprehensive/
├── NES/
│   ├── Super Mario Bros. (USA).nes
│   ├── Super Mario Bros. (Japan).nes
│   ├── Super Mario Bros. (Europe).nes
│   ├── Zelda II (USA).nes
│   ├── Zelda II (Japan).nes
│   ├── Dragon Quest (Japan).nes
│   ├── Dragon Quest (USA).nes
│   └── to_delete/
├── SNES/
│   ├── Super Mario World (USA).smc
│   ├── Super Mario World (Japan).smc
│   ├── Secret of Mana (Japan).smc
│   └── to_delete/
├── GBA/
│   ├── Advance Wars (USA).gba
│   ├── Advance Wars (Japan).gba
│   └── to_delete/
├── PSX/
│   ├── Resident Evil (USA).iso
│   ├── Biohazard (Japan).iso
│   └── to_delete/
├── Compressed/
│   ├── Super Mario Bros Compressed (USA).zip
│   ├── Super Mario Bros Compressed (Europe).7z
│   └── to_delete/
└── Mixed_Formats/
    ├── Super Mario Bros. (USA).nes
    ├── Super Mario Bros. (USA).zip
    └── to_delete/
```

## Test Scenarios Covered

### 1. Multiple Regions
- **Super Mario Bros**: USA, Japan, Europe versions
- **Zelda II**: USA, Japan versions
- **Advance Wars**: USA, Japan versions

### 2. Japanese-Only Games
- **Dragon Quest**: Japan version only (should be kept)
- **Secret of Mana**: Japan version only (should be kept)
- **Biohazard series**: Japan versions only (should be kept)

### 3. Alternative Names
- **Resident Evil (USA)** vs **Biohazard (Japan)**: Same game, different names
- Tests the IGDB API integration for name matching

### 4. Compressed Formats
- **ZIP files**: `.zip` compression
- **7Z files**: `.7z` compression
- Tests compression format detection and handling

### 5. Mixed Formats
- Same game in both uncompressed (`.nes`) and compressed (`.zip`) formats
- Tests format preference and duplicate detection

### 6. Different Platforms
- **NES**: `.nes` files
- **SNES**: `.smc` files
- **GBA**: `.gba` files
- **PSX**: `.iso` files

## Running the Tests

### 1. Basic Test Script
Run the comprehensive test script:
```bash
python test_comprehensive_cleanup.py
```

This script will:
- Test all directories with `--dry-run` flag
- Test each platform separately
- Test compressed formats
- Test mixed formats
- Test move-to-folder functionality
- Test API integration

### 2. Manual Testing

#### Dry Run (Preview Only)
```bash
# Test all ROMs
python rom_cleanup.py test_roms_comprehensive --dry-run

# Test specific platform
python rom_cleanup.py test_roms_comprehensive/NES --dry-run
python rom_cleanup.py test_roms_comprehensive/SNES --dry-run
python rom_cleanup.py test_roms_comprehensive/GBA --dry-run
python rom_cleanup.py test_roms_comprehensive/PSX --dry-run
```

#### Move to Folder (Safe Cleanup)
```bash
# Move files to to_delete folders instead of deleting
python rom_cleanup.py test_roms_comprehensive --move-to-folder
```

#### GUI Testing
```bash
python rom_cleanup_gui.py
```
Then select the `test_roms_comprehensive` directory in the GUI.

## Expected Results

### Files That Should Be Removed
- **Super Mario Bros**: Keep USA, remove Japan and Europe
- **Zelda II**: Keep USA, remove Japan
- **Advance Wars**: Keep USA, remove Japan

### Files That Should Be Kept
- **Dragon Quest (Japan)**: Keep (Japanese-only game)
- **Secret of Mana (Japan)**: Keep (Japanese-only game)
- **Biohazard (Japan)**: Keep (Japanese-only game)
- **Resident Evil (USA)**: Keep (different name, same game)

### API Integration Testing
The tool should:
- Query IGDB API for game information
- Match alternative names (Biohazard ↔ Resident Evil)
- Cache results for faster subsequent runs

## Test Features

### 1. Region Detection
Tests the `get_region()` function with various naming patterns:
- `(USA)`, `(Japan)`, `(Europe)`
- `[USA]`, `[Japan]`, `[Europe]`
- `(U)`, `(J)`, `(E)`

### 2. Base Name Extraction
Tests the `get_base_name()` function:
- Removes region tags
- Removes revision info
- Handles different naming conventions

### 3. Duplicate Detection
Tests finding duplicates across:
- Different regions
- Different formats (compressed vs uncompressed)
- Different naming conventions

### 4. Platform Mapping
Tests the `PLATFORM_MAPPING` dictionary:
- `.nes` → NES (platform ID 18)
- `.smc` → SNES (platform ID 19)
- `.gba` → GBA (platform ID 24)
- `.iso` → PSX (platform IDs 8, 9)

### 5. API Integration
Tests IGDB API queries:
- Game name matching
- Alternative name detection
- Platform-specific searches
- Caching functionality

## Cleaning Up

After testing, you can remove the test files:
```bash
# PowerShell
Remove-Item -Recurse -Force test_roms_comprehensive

# Or manually delete the directory
```

## Troubleshooting

### Common Issues

1. **"No ROMs found"**
   - Check that the test directory exists
   - Verify file extensions are supported

2. **API errors**
   - Check that IGDB credentials are set
   - Verify internet connection

3. **Permission errors**
   - Run as administrator if needed
   - Check file permissions

### Debug Mode
For detailed output, you can modify the test script to include debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Extending the Tests

To add more test scenarios:

1. **Add new dummy ROMs** to the appropriate directory
2. **Update the test script** to include new test cases
3. **Document expected behavior** in this README

### Example: Adding a New Platform
```bash
# Create directory
mkdir test_roms_comprehensive/N64

# Add dummy ROMs
echo "# Dummy N64 ROM" > test_roms_comprehensive/N64/Super Mario 64 (USA).n64
echo "# Dummy N64 ROM" > test_roms_comprehensive/N64/Super Mario 64 (Japan).n64

# Update test script
# Add N64 test case to test_comprehensive_cleanup.py
```

This comprehensive test setup ensures that all features of the ROM cleanup tool are thoroughly tested with realistic scenarios. 