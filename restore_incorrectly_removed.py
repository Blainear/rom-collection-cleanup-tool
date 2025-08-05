#!/usr/bin/env python3
"""
ROM Collection Restoration Script

This script helps restore ROM files that were incorrectly moved by the previous
version of the cleanup tool. It identifies and moves back:

1. Multi-disc games that were broken apart
2. Same-region versions that should have been kept
3. Rev 1 and special editions that have value

Usage: python restore_incorrectly_removed.py [rom_directory]
"""

import argparse
import logging
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from rom_utils import get_base_name, get_region, get_version_info, is_multi_disc_game

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def find_removed_duplicates_folder(rom_directory: Path) -> Path:
    """Find the removed_duplicates folder."""
    possible_names = ["removed_duplicates", "to_delete"]

    for name in possible_names:
        removed_folder = rom_directory / name
        if removed_folder.exists():
            return removed_folder

    raise FileNotFoundError("Could not find removed_duplicates or to_delete folder")


def analyze_removed_files(removed_folder: Path) -> Dict[str, List[Path]]:
    """Analyze removed files and group by base game name."""
    logger.info(f"Analyzing files in: {removed_folder}")

    # Get all ROM files
    rom_extensions = {
        ".zip",
        ".bin",
        ".cue",
        ".iso",
        ".chd",
        ".nes",
        ".snes",
        ".gb",
        ".gba",
        ".nds",
        ".md",
        ".gen",
    }
    rom_files = []

    for file_path in removed_folder.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in rom_extensions:
            rom_files.append(file_path)

    logger.info(f"Found {len(rom_files)} ROM files in removed folder")

    # Group by base name
    groups = defaultdict(list)
    for file_path in rom_files:
        base_name = get_base_name(file_path.name)
        groups[base_name].append(file_path)

    return dict(groups)


def identify_files_to_restore(
    removed_groups: Dict[str, List[Path]], main_directory: Path
) -> List[Path]:
    """Identify which files should be restored."""
    to_restore = []

    logger.info("Analyzing removed files for restoration...")

    for base_name, removed_files in removed_groups.items():
        logger.info(f"\\nAnalyzing: {base_name} ({len(removed_files)} removed files)")

        # Check what's still in the main directory
        remaining_files = []
        for file_path in main_directory.rglob("*"):
            if (
                file_path.is_file()
                and get_base_name(file_path.name) == base_name
                and file_path.parent.name not in ["removed_duplicates", "to_delete"]
            ):
                remaining_files.append(file_path)

        logger.info(f"  Remaining in main directory: {len(remaining_files)}")
        for f in remaining_files:
            logger.info(f"    {f.name}")

        # Check for multi-disc games
        all_filenames = [f.name for f in removed_files + remaining_files]
        if is_multi_disc_game(all_filenames):
            logger.info("  🎮 MULTI-DISC GAME DETECTED!")
            logger.info("  ✅ Restoring all removed discs")
            to_restore.extend(removed_files)
            continue

        # Check for same-region duplicates that shouldn't have been removed
        regions_removed = set()
        regions_remaining = set()

        for f in removed_files:
            regions_removed.add(get_region(f.name))
        for f in remaining_files:
            regions_remaining.add(get_region(f.name))

        logger.info(f"  Regions removed: {regions_removed}")
        logger.info(f"  Regions remaining: {regions_remaining}")

        # If only same-region files were removed, restore them
        if len(regions_removed) == 1 and len(regions_remaining) <= 1:
            if not regions_remaining or regions_removed == regions_remaining:
                logger.info("  ❌ SAME-REGION REMOVAL DETECTED!")
                logger.info("  ✅ Restoring same-region versions")
                to_restore.extend(removed_files)
                continue

        # Check for valuable versions (Rev 1, Special Editions)
        for removed_file in removed_files:
            version_info = get_version_info(removed_file.name)
            if any(
                keyword in version_info.lower()
                for keyword in [
                    "rev 1",
                    "revision 1",
                    "special",
                    "limited",
                    "premium",
                    "deluxe",
                ]
            ):
                logger.info(f"  💎 VALUABLE VERSION: {removed_file.name}")
                logger.info(f"     Version info: {version_info}")
                logger.info("  ✅ Restoring valuable version")
                to_restore.append(removed_file)

    return to_restore


def restore_files(
    files_to_restore: List[Path], main_directory: Path, dry_run: bool = True
) -> int:
    """Restore files back to the main directory."""
    logger.info(
        f"\\n{'DRY RUN: ' if dry_run else ''}Restoring {len(files_to_restore)} files..."
    )

    restored_count = 0

    for file_path in files_to_restore:
        # Calculate destination path
        relative_path = file_path.relative_to(file_path.parent.parent)
        dest_path = main_directory / relative_path.name

        # Avoid overwriting existing files
        if dest_path.exists():
            counter = 1
            stem = dest_path.stem
            suffix = dest_path.suffix
            while dest_path.exists():
                dest_path = dest_path.parent / f"{stem}_restored_{counter}{suffix}"
                counter += 1

        logger.info(
            f"  {'WOULD RESTORE' if dry_run else 'RESTORING'}: {file_path.name}"
        )
        logger.info(f"    → {dest_path}")

        if not dry_run:
            try:
                # Create destination directory if needed
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Move the file
                shutil.move(str(file_path), str(dest_path))
                restored_count += 1
            except Exception as e:
                logger.error(f"    ERROR: {e}")
        else:
            restored_count += 1

    return restored_count


def main() -> int:
    """Main restoration script."""
    parser = argparse.ArgumentParser(
        description="Restore ROM files that were incorrectly removed"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="ROM directory path (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be restored without actually moving files",
    )

    args = parser.parse_args()

    try:
        rom_directory = Path(args.directory).resolve()
        logger.info(f"ROM directory: {rom_directory}")

        # Find removed files folder
        removed_folder = find_removed_duplicates_folder(rom_directory)
        logger.info(f"Found removed files in: {removed_folder}")

        # Analyze removed files
        removed_groups = analyze_removed_files(removed_folder)

        if not removed_groups:
            logger.info("No ROM files found in removed folder")
            return 0

        # Identify files to restore
        files_to_restore = identify_files_to_restore(removed_groups, rom_directory)

        if not files_to_restore:
            logger.info("\\n✅ No files need restoration - removal appears correct")
            return 0

        # Restore files
        restored_count = restore_files(files_to_restore, rom_directory, args.dry_run)

        if args.dry_run:
            logger.info(f"\\n[DRY RUN] Would restore {restored_count} files")
            logger.info("Run without --dry-run to actually restore files")
        else:
            logger.info(f"\\n✅ Successfully restored {restored_count} files")

        return 0

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
