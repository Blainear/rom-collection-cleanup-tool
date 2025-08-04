#!/usr/bin/env python3
"""
ROM Collection Cleanup Script

This script scans ROM files and removes Japanese versions when both
Japanese and USA releases exist, while keeping Japanese-only games.

Usage: python rom_cleanup.py [rom_directory] [--dry-run] [--move-to-folder] [--verbose] [--quiet]

Options:
  --dry-run         Preview what would be processed without making changes
  --move-to-folder  Move files to 'to_delete' subfolder instead of deleting
  --verbose         Show detailed debug output
  --quiet           Only show warnings and errors
"""

import argparse
import json
import logging
import os
import shutil
import sys
import time
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from rom_utils import get_base_name, get_region

try:
    import requests
except ImportError:
    requests = None

# Common ROM file extensions
DEFAULT_ROM_EXTENSIONS = {
    # Archive formats
    ".zip",
    ".7z",
    ".rar",
    # Nintendo systems
    ".nes",
    ".snes",
    ".smc",
    ".sfc",
    ".gb",
    ".gbc",
    ".gba",
    ".nds",
    ".3ds",
    ".cia",
    ".n64",
    ".z64",
    ".v64",
    ".ndd",
    ".gcm",
    ".gcz",
    ".rvz",
    ".wbfs",
    ".xci",
    ".nsp",
    ".vb",
    ".lnx",
    ".ngp",
    ".ngc",
    # Sega systems
    ".md",
    ".gen",
    ".smd",
    ".gg",
    ".sms",
    ".32x",
    ".sat",
    ".gdi",
    # Sony systems
    ".bin",
    ".iso",
    ".cue",
    ".chd",
    ".pbp",
    ".cso",
    ".ciso",
    # PC Engine/TurboGrafx
    ".pce",
    ".sgx",
    # Atari systems
    ".a26",
    ".a78",
    ".st",
    ".d64",
    # Other retro systems
    ".col",
    ".int",
    ".vec",
    ".ws",
    ".wsc",
    # Disk images
    ".img",
    ".ima",
    ".dsk",
    ".adf",
    ".mdf",
    ".nrg",
    # Tape formats
    ".tap",
    ".tzx",
    # Spectrum formats
    ".sna",
    ".z80",
}

logger = logging.getLogger(__name__)

GAME_CACHE = {}
CACHE_FILE = Path("game_cache.json")
IGDB_CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
IGDB_ACCESS_TOKEN = os.getenv("IGDB_ACCESS_TOKEN")

PLATFORM_MAPPING = {
    # Nintendo systems
    ".nes": [18],
    ".snes": [19],
    ".smc": [19],
    ".sfc": [19],
    ".gb": [33],
    ".gbc": [22],
    ".gba": [24],
    ".nds": [20],
    ".3ds": [37],
    ".cia": [37],
    ".n64": [4],
    ".z64": [4],
    ".v64": [4],
    ".ndd": [4],
    ".gcm": [21],
    ".gcz": [21],
    ".rvz": [21],
    ".wbfs": [5],  # GameCube and Wii
    ".xci": [130],
    ".nsp": [130],  # Nintendo Switch
    ".vb": [87],
    ".lnx": [28],
    ".ngp": [119],
    ".ngc": [120],
    # Sega systems
    ".md": [29],
    ".gen": [29],
    ".smd": [29],
    ".gg": [35],
    ".sms": [64],
    ".32x": [30],
    ".sat": [32],
    ".gdi": [23],  # Saturn and Dreamcast
    # Sony systems
    ".iso": [7, 8, 9],
    ".bin": [7, 8, 9],
    ".cue": [7, 8, 9],
    ".chd": [7, 8, 9],
    ".pbp": [8],
    ".cso": [8],
    ".ciso": [8],  # PlayStation systems
    ".mdf": [8],
    ".nrg": [8],
    # PC Engine/TurboGrafx
    ".pce": [86],
    ".sgx": [86],
    # Atari systems
    ".a26": [59],
    ".a78": [60],
    ".st": [63],
    # Other systems
    ".col": [68],
    ".int": [67],
    ".vec": [70],
    ".ws": [57],
    ".wsc": [57],
}


def load_game_cache() -> None:
    """Load game database cache from file."""
    global GAME_CACHE
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                GAME_CACHE = json.load(f)
            logger.info("Loaded %d games from cache", len(GAME_CACHE))
        except (json.JSONDecodeError, IOError, OSError) as e:
            logger.warning("Could not load cache: %s", e)
            GAME_CACHE = {}


def save_game_cache() -> None:
    """Save game database cache to file."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(GAME_CACHE, f, ensure_ascii=False, indent=2)
    except (IOError, OSError) as e:
        logger.warning("Could not save cache: %s", e)


def query_igdb_game(
    game_name: str, file_extension: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Query IGDB for game information and alternative names."""
    if not requests:
        logger.debug("requests library not available - skipping IGDB lookup")
        return None

    if not IGDB_CLIENT_ID or not IGDB_ACCESS_TOKEN:
        logger.debug("IGDB credentials not configured - skipping API lookup")
        return None

    platform_filter = ""
    target_platforms = []
    if file_extension and file_extension.lower() in PLATFORM_MAPPING:
        target_platforms = PLATFORM_MAPPING[file_extension.lower()]
        platform_filter = f"where platforms = ({','.join(map(str, target_platforms))});"

    query = f"""
    search "{game_name}";
    fields name, alternative_names.name, platforms;
    {platform_filter}
    limit 20;
    """

    headers = {
        "Client-ID": IGDB_CLIENT_ID,
        "Authorization": f"Bearer {IGDB_ACCESS_TOKEN}",
        "Content-Type": "text/plain",
    }

    backoff = 0.5
    for attempt in range(3):
        try:
            response = requests.post(
                "https://api.igdb.com/v4/games",
                headers=headers,
                data=query.strip(),
                timeout=10,
            )

            if response.status_code == 429:
                time.sleep(backoff * (attempt + 1))
                continue

            response.raise_for_status()
            games = response.json()

            scored_matches = []

            for game in games:
                all_names = [game["name"]]
                if "alternative_names" in game:
                    all_names.extend([alt["name"] for alt in game["alternative_names"]])

                platform_bonus = 0
                if target_platforms and "platforms" in game:
                    game_platforms = [p for p in game["platforms"]]
                    if any(p in target_platforms for p in game_platforms):
                        platform_bonus = 0.2

                # Check all names for matches with improved logic
                best_match_score = 0
                best_match_name = None
                match_type = None

                for name in all_names:
                    ratio = SequenceMatcher(
                        None, game_name.lower(), name.lower()
                    ).ratio()

                    # More lenient thresholds for cross-language matching
                    if name == game["name"]:  # Main name
                        threshold = 0.7  # Lowered from 0.8
                        if ratio >= threshold:
                            final_score = ratio + platform_bonus
                            if final_score > best_match_score:
                                best_match_score = final_score
                                best_match_name = name
                                match_type = "main"
                    else:  # Alternative name - even more lenient
                        threshold = 0.25  # Lowered from 0.3 for cross-language matches
                        if ratio >= threshold:
                            final_score = ratio + platform_bonus
                            if final_score > best_match_score:
                                best_match_score = final_score
                                best_match_name = name
                                match_type = "alternative"

                if best_match_score > 0:
                    scored_matches.append(
                        {
                            "game": game,
                            "score": best_match_score,
                            "match_name": best_match_name,
                            "match_type": match_type,
                            "all_names": all_names,
                        }
                    )

            # Sort by score (highest first)
            scored_matches.sort(key=lambda x: x["score"], reverse=True)

            # Return best match
            if scored_matches:
                best_match = scored_matches[0]
                return {
                    "canonical_name": best_match["game"]["name"],
                    "alternative_names": best_match["all_names"],
                    "id": best_match["game"]["id"],
                    "match_score": best_match["score"],
                    "matched_on": best_match["match_name"],
                }

            break
        except requests.HTTPError as http_err:
            logger.warning("IGDB API HTTP error for '%s': %s", game_name, http_err)
            break
        except Exception as e:
            logger.warning("Warning: IGDB API error for '%s': %s", game_name, e)
            break
        finally:
            # Rate limiting
            time.sleep(0.25)  # IGDB allows 4 requests per second

    return None


def normalize_canonical_name(name: str) -> str:
    """
    Basic normalization - just lowercase and strip.
    Let the IGDB API handle the intelligent matching.
    """
    return name.lower().strip()


def get_canonical_name(game_name: str, file_extension: Optional[str] = None) -> str:
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
        canonical = normalize_canonical_name(igdb_result["canonical_name"])
        GAME_CACHE[cache_key] = canonical
        return canonical

    # Fallback: check for obvious matches in already cached games
    best_match = None
    best_ratio = 0.0

    for cached_key, cached_canonical in GAME_CACHE.items():
        if file_extension and not cached_key.endswith(file_extension or "unknown"):
            continue

        cached_name = cached_key.split("_")[0]  # Remove file extension part
        ratio = SequenceMatcher(None, game_name_clean, cached_name).ratio()

        # More lenient threshold for cross-language matching
        if ratio > best_ratio and ratio > 0.75:  # Lowered from 0.85
            best_ratio = ratio
            best_match = cached_canonical

    if best_match:
        GAME_CACHE[cache_key] = best_match
        return best_match

    # No match found, cache and return normalized original name
    canonical = normalize_canonical_name(game_name_clean)
    GAME_CACHE[cache_key] = canonical
    return canonical


def scan_roms(
    directory: str, rom_extensions: Set[str]
) -> Dict[str, List[Tuple[Path, str, str]]]:
    """
    Scan directory for ROM files and group them by canonical name.

    Args:
        directory: Path to the directory to scan
        rom_extensions: Set of file extensions to consider as ROM files

    Returns:
        Dictionary mapping canonical names to lists of
        (file_path, region, original_name) tuples
    """
    rom_groups = defaultdict(list)

    directory = Path(directory)

    load_game_cache()

    processed_files = 0

    logger.info("Processing ROM files...")

    for file_path in directory.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in rom_extensions:
            filename = file_path.name
            base_name = get_base_name(filename)
            file_extension = file_path.suffix.lower()
            canonical_name = get_canonical_name(base_name, file_extension)
            region = get_region(filename)

            rom_groups[canonical_name].append((file_path, region, base_name))

            processed_files += 1
            if processed_files % 10 == 0:
                logger.debug("  Processed %d files...", processed_files)

    logger.info("Processed %d ROM files in total.", processed_files)

    save_game_cache()

    # Debug output: show game groupings
    logger.debug("\nGame groupings after processing:")
    for canonical_name, roms in rom_groups.items():
        if len(roms) > 1:
            logger.debug("  🎮 %s:", canonical_name)
            for file_path, region, original_name in roms:
                logger.debug(
                    "    - %s (%s) -> %s", original_name, region, file_path.name
                )

    return rom_groups


def find_duplicates_to_remove(
    rom_groups: Dict[str, List[Tuple[Path, str, str]]],
) -> List[Path]:
    """
    Find Japanese ROMs to remove when both Japanese and USA versions exist.

    Args:
        rom_groups: Dictionary mapping canonical names to ROM file tuples

    Returns:
        List of file paths to remove
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

        # If we have both Japanese and USA versions,
        # verify they are actually the same game
        if "japan" in regions and "usa" in regions:
            # Trust the canonical name from API - if they have the same
            # canonical name, they're the same game
            # Only do string similarity check as a fallback for non-API matches
            max_ratio = 0.0
            for _, j_name in regions["japan"]:
                for _, u_name in regions["usa"]:
                    ratio = SequenceMatcher(
                        None, j_name.lower(), u_name.lower()
                    ).ratio()
                    if ratio > max_ratio:
                        max_ratio = ratio

            # If we have multiple original names (like Biohazard vs Resident Evil),
            # trust that the API correctly identified them as the same game
            if len(original_names) > 1 and max_ratio < 0.6:
                logger.info("Game: %s", canonical_name)
                logger.info(
                    "  📋 API matched variants: %s", ", ".join(sorted(original_names))
                )
                logger.info("  ✅ Trusting API match - removing Japanese version(s)")
                # Remove Japanese versions when USA versions exist (trust API)
                japanese_files = [file_path for file_path, _ in regions["japan"]]
                to_remove.extend(japanese_files)
                logger.info(
                    "  ✅ Keeping USA version(s): %s",
                    [path.name for path, _ in regions["usa"]],
                )
                logger.info(
                    "  ❌ Removing Japanese version(s): %s",
                    [path.name for path, _ in regions["japan"]],
                )
                logger.info("")
            elif max_ratio < 0.6:
                logger.info("Game: %s", canonical_name)
                if len(original_names) > 1:
                    logger.info(
                        "  📋 Matched variants with low similarity: %s",
                        ", ".join(sorted(original_names)),
                    )
                logger.info(
                    "  ⚠️ Low name similarity (%.2f) - keeping all versions", max_ratio
                )
                logger.info("")
                continue
            else:
                # Remove Japanese versions when USA versions exist
                japanese_files = [file_path for file_path, _ in regions["japan"]]
                to_remove.extend(japanese_files)

                logger.info("Game: %s", canonical_name)
                if len(original_names) > 1:
                    logger.info(
                        "  📋 Matched regional variants: %s",
                        ", ".join(sorted(original_names)),
                    )
                logger.info(
                    "  ✅ Keeping USA version(s): %s",
                    [path.name for path, _ in regions["usa"]],
                )
                logger.info(
                    "  ❌ Removing Japanese version(s): %s",
                    [path.name for path, _ in regions["japan"]],
                )
                logger.info("")

        # If we have Japanese and Europe but no USA, keep everything
        elif "japan" in regions and "europe" in regions and "usa" not in regions:
            if len(original_names) > 1:
                logger.info(
                    "Game: %s - 📋 Matched variants: %s",
                    canonical_name,
                    ", ".join(sorted(original_names)),
                )
            logger.info(
                "  ✅ Keeping both Japanese and European versions (no USA release)"
            )

        # If we have only Japanese versions, keep them
        elif "japan" in regions and len(regions) == 1:
            if len(original_names) > 1:
                logger.info(
                    "Game: %s - 📋 Matched variants: %s",
                    canonical_name,
                    ", ".join(sorted(original_names)),
                )
            logger.info("  ✅ Keeping Japanese-only release")

    return to_remove


def move_to_safe_folder(rom_directory: str, to_remove: List[Path]) -> int:
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
            logger.info("  Moved: %s -> %s", file_path, dest_path)
            moved_count += 1
        except PermissionError as e:
            logger.error("  Permission denied moving %s: %s", file_path, e)
        except FileNotFoundError as e:
            logger.error("  File not found: %s: %s", file_path, e)
        except OSError as e:
            logger.error("  OS error moving %s: %s", file_path, e)
        except ValueError as e:
            logger.error("  Path error with %s: %s", file_path, e)
        except Exception as e:
            logger.error("  Unexpected error moving %s: %s", file_path, e)

    return moved_count


def main() -> int:
    """Main entry point for the ROM cleanup script."""
    parser = argparse.ArgumentParser(
        description="Clean up ROM collection by removing Japanese duplicates"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory containing ROM files (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be removed without actually deleting files",
    )
    parser.add_argument(
        "--move-to-folder",
        action="store_true",
        help='Move files to a "to_delete" subfolder instead of deleting them',
    )
    parser.add_argument(
        "--extensions",
        help="Comma-separated list of additional file extensions to consider",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show debug output",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show warnings and errors",
    )

    args = parser.parse_args()

    if args.verbose and args.quiet:
        parser.error("--verbose and --quiet cannot be used together")

    log_level = (
        logging.DEBUG if args.verbose else logging.WARNING if args.quiet else logging.INFO
    )
    logging.basicConfig(level=log_level, format="%(message)s")

    if not os.path.exists(args.directory):
        logger.error("Error: Directory '%s' does not exist", args.directory)
        return 1

    rom_extensions = set(DEFAULT_ROM_EXTENSIONS)

    if args.extensions:
        custom_extensions = set()
        for ext in args.extensions.split(","):
            ext = ext.strip().lower()
            ext = ext if ext.startswith(".") else "." + ext
            custom_extensions.add(ext)
        rom_extensions.update(custom_extensions)

    logger.info("Scanning ROM files in: %s", os.path.abspath(args.directory))
    logger.info("Looking for extensions: %s", ", ".join(sorted(rom_extensions)))

    # Check IGDB API availability
    if not IGDB_CLIENT_ID or not IGDB_ACCESS_TOKEN:
        logger.warning("⚠️  IGDB credentials missing - basic name matching only")
        logger.info(
            "   For better matching of regional variants, set IGDB_CLIENT_ID and IGDB_ACCESS_TOKEN"
        )
        logger.info("   See README_API_CREDENTIALS.md for setup instructions")
    elif requests:
        logger.info("✅ IGDB API configured - enhanced name matching enabled")
    else:
        logger.warning("⚠️  'requests' library not found - install with: pip install requests")
    logger.info("")

    rom_groups = scan_roms(args.directory, rom_extensions)

    if not rom_groups:
        logger.info("No ROM files found in the specified directory.")
        return 0

    logger.info("Found %d unique games", len(rom_groups))
    logger.info("%s", "=" * 50)

    to_remove = find_duplicates_to_remove(rom_groups)

    if not to_remove:
        logger.info("No Japanese duplicates found to remove.")
        return 0

    logger.info("%s", "=" * 50)
    logger.info("Summary: %d Japanese ROM(s) to remove", len(to_remove))

    if args.dry_run:
        logger.info("\n[DRY RUN] Files that would be processed:")
        for file_path in to_remove:
            logger.info("  %s", file_path)
        if args.move_to_folder:
            logger.info(
                "\nRe-run without --dry-run to move these files to 'to_delete' folder."
            )
        else:
            logger.info("\nRe-run without --dry-run to actually delete these files.")
            logger.info(
                "Or use --move-to-folder to move them to a safe folder for review."
            )
    elif args.move_to_folder:
        logger.info(
            "\nMoving files to '%s/to_delete' folder for safe review...",
            args.directory,
        )
        moved_count = move_to_safe_folder(args.directory, to_remove)
        logger.info("\nSuccessfully moved %d files to 'to_delete' folder.", moved_count)
        logger.info(
            "Review the files in '%s/to_delete' and delete the folder when ready.",
            args.directory,
        )
    else:
        logger.info("\nRemoving files...")
        removed_count = 0
        for file_path in to_remove:
            try:
                file_path.unlink()
                logger.info("  Removed: %s", file_path)
                removed_count += 1
            except PermissionError as e:
                logger.error("  Permission denied removing %s: %s", file_path, e)
            except FileNotFoundError:
                logger.warning("  File not found (already removed?): %s", file_path)
            except OSError as e:
                logger.error("  OS error removing %s: %s", file_path, e)
            except Exception as e:
                logger.error("  Unexpected error removing %s: %s", file_path, e)

        logger.info("\nSuccessfully removed %d files.", removed_count)

    return 0


if __name__ == "__main__":
    sys.exit(main())
