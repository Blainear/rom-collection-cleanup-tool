#!/usr/bin/env python3
"""
ROM Collection Cleanup Script

This script scans ROM files and removes Japanese versions when both 
Japanese and USA releases exist, while keeping Japanese-only games.

Usage: python rom_cleanup.py [rom_directory] [--dry-run] [--move-to-folder]

Options:
  --dry-run         Preview what would be processed without making changes
  --move-to-folder  Move files to 'to_delete' subfolder instead of deleting
"""

import os
import re
import sys
import argparse
import shutil
import json
import time
import hashlib
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

try:
    import requests
except ImportError:
    requests = None

# Common ROM file extensions
ROM_EXTENSIONS = {'.zip', '.7z', '.rar', '.nes', '.snes', '.smc', '.sfc', 
                 '.gb', '.gbc', '.gba', '.nds', '.n64', '.z64', '.v64',
                 '.md', '.gen', '.smd', '.bin', '.iso', '.cue', '.chd',
                 '.pbp', '.cso', '.gcz', '.wbfs', '.rvz',
                  '.gcm', '.ciso', '.mdf', '.nrg'}

# Region patterns - matches common ROM naming conventions
REGION_PATTERNS = {
    'japan': [r'\(J\)', r'\(Japan\)', r'\(JP\)', r'\(JPN\)', r'\[J\]', r'\[Japan\]'],
    'usa': [r'\(U\)', r'\(USA\)', r'\(US\)', r'\[U\]', r'\[USA\]', r'\[US\]'],
    'europe': [r'\(E\)', r'\(Europe\)', r'\(EUR\)', r'\[E\]', r'\[Europe\]'],
    'world': [r'\(W\)', r'\(World\)', r'\[W\]', r'\[World\]']
}

GAME_CACHE = {}
CACHE_FILE = Path("game_cache.json")
IGDB_CLIENT_ID = os.getenv('IGDB_CLIENT_ID', '')
IGDB_ACCESS_TOKEN = os.getenv('IGDB_ACCESS_TOKEN', '')

PLATFORM_MAPPING = {
    '.nes': [18], '.snes': [19], '.smc': [19], '.sfc': [19],
    '.gb': [33], '.gbc': [22], '.gba': [24], '.nds': [20],
    '.n64': [4], '.z64': [4], '.v64': [4],
    '.md': [29], '.gen': [29], '.smd': [29],
    '.gcm': [21], '.gcz': [21], '.rvz': [21],
    '.iso': [8, 9], '.mdf': [8], '.nrg': [8],
}

def get_region(filename):
    """Extract region from filename based on common ROM naming patterns."""
    filename_upper = filename.upper()
    
    for region, patterns in REGION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, filename_upper):
                return region
    return 'unknown'

def get_base_name(filename):
    """
    Extract the base game name by removing region tags, revision info, etc.
    """
    # Remove file extension
    base = os.path.splitext(filename)[0]
    
    # Remove common ROM tags in parentheses and brackets
    # This regex removes content in (), [], and common revision patterns
    base = re.sub(r'\s*[\(\[].*?[\)\]]', '', base)
    base = re.sub(r'\s*\(.*?\)', '', base)
    base = re.sub(r'\s*\[.*?\]', '', base)
    
    # Remove common revision/version patterns
    base = re.sub(r'\s*(Rev|v|Ver|Version)\s*\d+.*$', '', base, flags=re.IGNORECASE)
    base = re.sub(r'\s*-\s*\d+$', '', base)  # Remove trailing numbers like "- 1"
    
    # Clean up extra whitespace
    base = re.sub(r'\s+', ' ', base).strip()
    
    return base

def load_game_cache():
    """Load game database cache from file."""
    global GAME_CACHE
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                GAME_CACHE = json.load(f)
            print(f"Loaded {len(GAME_CACHE)} games from cache")
        except Exception as e:
            print(f"Warning: Could not load cache: {e}")
            GAME_CACHE = {}

def save_game_cache():
    """Save game database cache to file."""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(GAME_CACHE, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Warning: Could not save cache: {e}")

def query_igdb_game(game_name, file_extension=None):
    """Query IGDB for game information and alternative names."""
    if not requests or not IGDB_CLIENT_ID or not IGDB_ACCESS_TOKEN:
        return None
    
    try:
        platform_filter = ""
        target_platforms = []
        if file_extension and file_extension.lower() in PLATFORM_MAPPING:
            target_platforms = PLATFORM_MAPPING[file_extension.lower()]
            platform_filter = f"where platforms = ({','.join(map(str, target_platforms))});"

        query = f'''
        search "{game_name}";
        fields name, alternative_names.name, platforms;
        {platform_filter}
        limit 15;
        '''
        
        headers = {
            'Client-ID': IGDB_CLIENT_ID,
            'Authorization': f'Bearer {IGDB_ACCESS_TOKEN}',
            'Content-Type': 'text/plain'
        }
        
        response = requests.post(
            'https://api.igdb.com/v4/games',
            headers=headers,
            data=query.strip(),
            timeout=10
        )
        
        if response.status_code == 200:
            games = response.json()
            
            scored_matches = []
            
            for game in games:
                all_names = [game['name']]
                if 'alternative_names' in game:
                    all_names.extend([alt['name'] for alt in game['alternative_names']])
                
                platform_bonus = 0
                if target_platforms and 'platforms' in game:
                    game_platforms = [p for p in game['platforms']]
                    if any(p in target_platforms for p in game_platforms):
                        platform_bonus = 0.2
                
                # Check all names for matches
                best_match_score = 0
                best_match_name = None
                match_type = None
                
                for name in all_names:
                    ratio = SequenceMatcher(None, game_name.lower(), name.lower()).ratio()
                    
                    # Different thresholds for main name vs alternatives
                    if name == game['name']:  # Main name
                        threshold = 0.8
                        if ratio >= threshold:
                            final_score = ratio + platform_bonus
                            if final_score > best_match_score:
                                best_match_score = final_score
                                best_match_name = name
                                match_type = "main"
                    else:  # Alternative name - lower threshold
                        threshold = 0.3
                        if ratio >= threshold:
                            final_score = ratio + platform_bonus
                            if final_score > best_match_score:
                                best_match_score = final_score
                                best_match_name = name
                                match_type = "alternative"
                
                if best_match_score > 0:
                    scored_matches.append({
                        'game': game,
                        'score': best_match_score,
                        'match_name': best_match_name,
                        'match_type': match_type,
                        'all_names': all_names
                    })
            
            # Sort by score (highest first)
            scored_matches.sort(key=lambda x: x['score'], reverse=True)
            
            # Return best match
            if scored_matches:
                best_match = scored_matches[0]
                return {
                    'canonical_name': best_match['game']['name'],
                    'alternative_names': best_match['all_names'],
                    'id': best_match['game']['id'],
                    'match_score': best_match['score'],
                    'matched_on': best_match['match_name']
                }
        
        # Rate limiting
        time.sleep(0.25)  # IGDB allows 4 requests per second
        
    except Exception as e:
        print(f"Warning: IGDB API error for '{game_name}': {e}")
    
    return None

def get_canonical_name(game_name, file_extension=None):
    """
    Get canonical name for a game using database lookup and fuzzy matching.
    """
    game_name_clean = game_name.strip().lower()
    
    # Check cache first
    cache_key = f"{game_name_clean}_{file_extension or 'unknown'}"
    if cache_key in GAME_CACHE:
        return GAME_CACHE[cache_key]
    
    # Try IGDB API lookup
    igdb_result = query_igdb_game(game_name, file_extension)
    if igdb_result:
        canonical = igdb_result['canonical_name'].lower()
        GAME_CACHE[cache_key] = canonical
        return canonical
    
    # Fallback: check for obvious matches in already cached games
    best_match = None
    best_ratio = 0.0
    
    for cached_key, cached_canonical in GAME_CACHE.items():
        if file_extension and not cached_key.endswith(file_extension or 'unknown'):
            continue
            
        cached_name = cached_key.split('_')[0]  # Remove file extension part
        ratio = SequenceMatcher(None, game_name_clean, cached_name).ratio()
        
        if ratio > best_ratio and ratio > 0.85:
            best_ratio = ratio
            best_match = cached_canonical
    
    if best_match:
        GAME_CACHE[cache_key] = best_match
        return best_match
    
    # No match found, cache and return normalized original name
    canonical = game_name_clean
    GAME_CACHE[cache_key] = canonical
    return canonical

def scan_roms(directory):
    """
    Scan directory for ROM files and group them by canonical name.
    Returns dict: {canonical_name: [(full_path, region, original_name), ...]}
    """
    rom_groups = defaultdict(list)
    
    directory = Path(directory)
    
    load_game_cache()
    
    total_files = 0
    processed_files = 0
    

    for file_path in directory.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in ROM_EXTENSIONS:
            total_files += 1
    
    print(f"Processing {total_files} ROM files...")
    

    for file_path in directory.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in ROM_EXTENSIONS:
            filename = file_path.name
            base_name = get_base_name(filename)
            file_extension = file_path.suffix.lower()
            canonical_name = get_canonical_name(base_name, file_extension)
            region = get_region(filename)
            
            rom_groups[canonical_name].append((file_path, region, base_name))
            
            processed_files += 1
            if processed_files % 10 == 0:
                print(f"  Processed {processed_files}/{total_files} files...")
    
    save_game_cache()
    
    return rom_groups

def find_duplicates_to_remove(rom_groups):
    """
    Find Japanese ROMs to remove when both Japanese and USA versions exist.
    Returns list of file paths to remove.
    """
    to_remove = []
    
    for canonical_name, roms in rom_groups.items():
        if len(roms) <= 1:
            continue
            
        # Group by region
        regions = defaultdict(list)
        original_names = set()
        for file_path, region, original_name in roms:
            regions[region].append((file_path, original_name))
            original_names.add(original_name)
        
        # If we have both Japanese and USA versions, mark Japanese for removal
        if 'japan' in regions and 'usa' in regions:
            # Remove Japanese versions when USA versions exist
            japanese_files = [file_path for file_path, _ in regions['japan']]
            to_remove.extend(japanese_files)
            
            print(f"Game: {canonical_name}")
            if len(original_names) > 1:
                print(f"  📋 Matched regional variants: {', '.join(sorted(original_names))}")
            print(f"  ✅ Keeping USA version(s): {[path.name for path, _ in regions['usa']]}")
            print(f"  ❌ Removing Japanese version(s): {[path.name for path, _ in regions['japan']]}")
            print()
        
        # If we have Japanese and Europe but no USA, keep everything
        elif 'japan' in regions and 'europe' in regions and 'usa' not in regions:
            if len(original_names) > 1:
                print(f"Game: {canonical_name} - 📋 Matched variants: {', '.join(sorted(original_names))}")
            print(f"  ✅ Keeping both Japanese and European versions (no USA release)")
        
        # If we have only Japanese versions, keep them
        elif 'japan' in regions and len(regions) == 1:
            if len(original_names) > 1:
                print(f"Game: {canonical_name} - 📋 Matched variants: {', '.join(sorted(original_names))}")
            print(f"  ✅ Keeping Japanese-only release")
    
    return to_remove

def move_to_safe_folder(rom_directory, to_remove):
    """
    Move ROMs to a 'to_delete' subfolder for safe review before deletion.
    Returns count of successfully moved files.
    """
    safe_folder = Path(rom_directory) / "to_delete"
    safe_folder.mkdir(exist_ok=True)
    
    moved_count = 0
    for file_path in to_remove:
        try:
            # Create relative path structure in safe folder
            rel_path = file_path.relative_to(Path(rom_directory))
            dest_path = safe_folder / rel_path
            
            # Create subdirectories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            shutil.move(str(file_path), str(dest_path))
            print(f"  Moved: {file_path} -> {dest_path}")
            moved_count += 1
        except Exception as e:
            print(f"  Error moving {file_path}: {e}")
    
    return moved_count

def main():
    parser = argparse.ArgumentParser(description='Clean up ROM collection by removing Japanese duplicates')
    parser.add_argument('directory', nargs='?', default='.', 
                       help='Directory containing ROM files (default: current directory)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview what would be removed without actually deleting files')
    parser.add_argument('--move-to-folder', action='store_true',
                       help='Move files to a "to_delete" subfolder instead of deleting them')
    parser.add_argument('--extensions', 
                       help='Comma-separated list of additional file extensions to consider')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist")
        return 1
    

    if args.extensions:
        custom_extensions = set()
        for ext in args.extensions.split(','):
            ext = ext.strip().lower()
            ext = ext if ext.startswith('.') else '.' + ext
            custom_extensions.add(ext)
        ROM_EXTENSIONS.update(custom_extensions)
    
    print(f"Scanning ROM files in: {os.path.abspath(args.directory)}")
    print(f"Looking for extensions: {', '.join(sorted(ROM_EXTENSIONS))}")
    print()
    

    rom_groups = scan_roms(args.directory)
    
    if not rom_groups:
        print("No ROM files found in the specified directory.")
        return 0
    
    print(f"Found {len(rom_groups)} unique games")
    print("=" * 50)
    

    to_remove = find_duplicates_to_remove(rom_groups)
    
    if not to_remove:
        print("No Japanese duplicates found to remove.")
        return 0
    
    print("=" * 50)
    print(f"Summary: {len(to_remove)} Japanese ROM(s) to remove")
    
    if args.dry_run:
        print("\n[DRY RUN] Files that would be processed:")
        for file_path in to_remove:
            print(f"  {file_path}")
        if args.move_to_folder:
            print("\nRe-run without --dry-run to move these files to 'to_delete' folder.")
        else:
            print("\nRe-run without --dry-run to actually delete these files.")
            print("Or use --move-to-folder to move them to a safe folder for review.")
    elif args.move_to_folder:
        print(f"\nMoving files to '{args.directory}/to_delete' folder for safe review...")
        moved_count = move_to_safe_folder(args.directory, to_remove)
        print(f"\nSuccessfully moved {moved_count} files to 'to_delete' folder.")
        print(f"Review the files in '{args.directory}/to_delete' and delete the folder when ready.")
    else:
        print("\nRemoving files...")
        removed_count = 0
        for file_path in to_remove:
            try:
                file_path.unlink()
                print(f"  Removed: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"  Error removing {file_path}: {e}")
        
        print(f"\nSuccessfully removed {removed_count} files.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())