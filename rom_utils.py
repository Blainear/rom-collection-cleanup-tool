"""
ROM utilities for file name parsing and region detection.

This module provides functions to extract base game names and detect
regions from ROM filenames following common naming conventions.
"""

import os
import re
from typing import Dict, List

# Region patterns - matches common ROM naming conventions
REGION_PATTERNS: Dict[str, List[str]] = {
    "japan": [r"\(J\)", r"\(Japan\)", r"\(JP\)", r"\(JPN\)", r"\[J\]", r"\[Japan\]"],
    "usa": [r"\(U\)", r"\(USA\)", r"\(US\)", r"\[U\]", r"\[USA\]", r"\[US\]"],
    "europe": [
        r"\(E\)",
        r"\(Europe\)",
        r"\(EUR\)",
        r"\[E\]",
        r"\[Europe\]",
        r"\[EUR\]",
    ],
    "world": [r"\(W\)", r"\(World\)", r"\[W\]", r"\[World\]"],
}


def get_version_info(filename: str) -> str:
    """
    Extract version/edition information from filename.

    Args:
        filename: The ROM filename to parse

    Returns:
        Version information string (Rev 1, Gentei Set, etc.)
    """
    if not filename or not isinstance(filename, str):
        return ""

    version_info = []

    # Check for revision info
    rev_match = re.search(
        r"\((Rev|Version|Ver|v)\s*\d+[^)]*\)", filename, re.IGNORECASE
    )
    if rev_match:
        version_info.append(rev_match.group(0).strip("()"))

    # Check for special editions
    edition_patterns = [
        r"\((Gentei Set|Limited Edition|Special Edition|Premium|Collectors|Deluxe)[^)]*\)",
        r"\((Beta|Proto|Demo|Sample|Taikenban)[^)]*\)",
        r"\((Value Plus|Greatest Hits|Platinum)[^)]*\)",
    ]

    for pattern in edition_patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            version_info.append(match.group(0).strip("()"))

    return " ".join(version_info)


def is_multi_disc_game(filenames: List[str]) -> bool:
    """
    Check if a list of filenames represents a multi-disc game.

    Args:
        filenames: List of ROM filenames

    Returns:
        True if this appears to be a multi-disc game
    """
    if len(filenames) < 2:
        return False

    disc_count = 0
    for filename in filenames:
        if re.search(r"\s*\((Disc|CD|Disk)\s*\d+[^)]*\)", filename, re.IGNORECASE):
            disc_count += 1

    # If more than half the files have disc numbers, it's likely multi-disc
    return disc_count >= len(filenames) * 0.6


def get_region(filename: str) -> str:
    """
    Extract region from filename based on common ROM naming patterns.

    Args:
        filename: The ROM filename to parse

    Returns:
        The detected region ('japan', 'usa', 'europe', 'world', or 'unknown')

    Examples:
        >>> get_region("Super Mario Bros. (USA).nes")
        'usa'
        >>> get_region("Final Fantasy (J).snes")
        'japan'
        >>> get_region("Sonic (E).md")
        'europe'
    """
    if not filename or not isinstance(filename, str):
        return "unknown"

    for region, patterns in REGION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return region
    return "unknown"


def get_base_name(filename: str) -> str:
    """
    Extract the base game name by removing region tags, revision info, etc.
    PRESERVES disc information to avoid breaking multi-disc games.

    Args:
        filename: The ROM filename to parse

    Returns:
        The cleaned base name of the game with disc info preserved

    Examples:
        >>> get_base_name("Super Mario Bros. (USA).nes")
        'Super Mario Bros.'
        >>> get_base_name("Final Fantasy IX (USA) (Disc 1).snes")
        'Final Fantasy IX (Disc 1)'
        >>> get_base_name("Final Fantasy (J) (Rev 2).snes")
        'Final Fantasy'
    """
    if not filename or not isinstance(filename, str):
        return ""

    # Remove file extension
    base = os.path.splitext(filename)[0]

    # PRESERVE disc information - extract it first
    disc_info = ""
    disc_match = re.search(r"\s*\((Disc|CD|Disk)\s*\d+[^)]*\)", base, re.IGNORECASE)
    if disc_match:
        disc_info = disc_match.group(0)
        # Remove the disc info from base temporarily to avoid duplication
        base = base.replace(disc_match.group(0), "")

    # Remove region tags specifically (not all parentheses)
    for region, patterns in REGION_PATTERNS.items():
        for pattern in patterns:
            base = re.sub(pattern, "", base, flags=re.IGNORECASE)

    # Remove other common tags but preserve disc info
    # Remove revision info
    base = re.sub(
        r"\s*\((Rev|Version|Ver|v)\s*\d+[^)]*\)", "", base, flags=re.IGNORECASE
    )
    # Remove version patterns like "Version 3" or "v2.0"
    base = re.sub(r"\s+Version\s+\d+", "", base, flags=re.IGNORECASE)
    base = re.sub(r"\s+v\d+\.\d+", "", base, flags=re.IGNORECASE)
    # Remove quality indicators
    base = re.sub(r"\s*[\[\(][!\+\-][\]\)]", "", base)
    # Remove other edition info
    base = re.sub(
        r"\s*\((Beta|Proto|Demo|Sample|Taikenban|Genteiban|Special|Limited|Premium)[^)]*\)",
        "",
        base,
        flags=re.IGNORECASE,
    )
    # Remove trailing numbers like "- 1" or " - 1"
    base = re.sub(r"\s*-\s*\d+$", "", base)
    base = re.sub(r"\s*-\s*\d+\s*$", "", base)

    # Clean up extra whitespace
    base = re.sub(r"\s+", " ", base).strip()

    # Add disc info back if it existed
    if disc_info:
        base += " " + disc_info.strip()

    return base
