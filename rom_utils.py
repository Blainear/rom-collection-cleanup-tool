"""
ROM utilities for file name parsing and region detection.

This module provides functions to extract base game names and detect
regions from ROM filenames following common naming conventions.
"""

import os
import re
from typing import Dict, List, Pattern

# Precompiled region patterns - matches common ROM naming conventions
REGION_PATTERNS: Dict[str, List[Pattern[str]]] = {
    "japan": [
        re.compile(r"\(J\)", re.IGNORECASE),
        re.compile(r"\(Japan\)", re.IGNORECASE),
        re.compile(r"\(JP\)", re.IGNORECASE),
        re.compile(r"\(JPN\)", re.IGNORECASE),
        re.compile(r"\[J\]", re.IGNORECASE),
        re.compile(r"\[Japan\]", re.IGNORECASE),
    ],
    "usa": [
        re.compile(r"\(U\)", re.IGNORECASE),
        re.compile(r"\(USA\)", re.IGNORECASE),
        re.compile(r"\(US\)", re.IGNORECASE),
        re.compile(r"\[U\]", re.IGNORECASE),
        re.compile(r"\[USA\]", re.IGNORECASE),
        re.compile(r"\[US\]", re.IGNORECASE),
    ],
    "europe": [
        re.compile(r"\(E\)", re.IGNORECASE),
        re.compile(r"\(Europe\)", re.IGNORECASE),
        re.compile(r"\(EUR\)", re.IGNORECASE),
        re.compile(r"\[E\]", re.IGNORECASE),
        re.compile(r"\[Europe\]", re.IGNORECASE),
        re.compile(r"\[EUR\]", re.IGNORECASE),
    ],
    "world": [
        re.compile(r"\(W\)", re.IGNORECASE),
        re.compile(r"\(World\)", re.IGNORECASE),
        re.compile(r"\[W\]", re.IGNORECASE),
        re.compile(r"\[World\]", re.IGNORECASE),
    ],
}

# Common patterns used across functions
DISC_PATTERN: Pattern[str] = re.compile(r"\s*\((Disc|CD|Disk)\s*\d+[^)]*\)", re.IGNORECASE)
REVISION_PATTERN: Pattern[str] = re.compile(
    r"\s*\((Rev|Version|Ver|v)\s*\d+[^)]*\)", re.IGNORECASE
)
VERSION_PATTERN: Pattern[str] = re.compile(r"\s+Version\s+\d+", re.IGNORECASE)
VDOT_PATTERN: Pattern[str] = re.compile(r"\s+v\d+\.\d+", re.IGNORECASE)
QUALITY_PATTERN: Pattern[str] = re.compile(r"\s*[\[\(][!\+\-][\]\)]")
EDITION_PATTERN: Pattern[str] = re.compile(
    r"\s*\((Beta|Proto|Demo|Sample|Taikenban|Genteiban|Special|Limited|Premium)[^)]*\)",
    re.IGNORECASE,
)
TRAILING_NUMBER_PATTERN: Pattern[str] = re.compile(r"\s*-\s*\d+\s*$")
WHITESPACE_PATTERN: Pattern[str] = re.compile(r"\s+")

# Edition patterns used for version info extraction
VERSION_EDITION_PATTERNS: List[Pattern[str]] = [
    re.compile(
        r"\((Gentei Set|Limited Edition|Special Edition|Premium|Collectors|Deluxe)[^)]*\)",
        re.IGNORECASE,
    ),
    re.compile(r"\((Beta|Proto|Demo|Sample|Taikenban)[^)]*\)", re.IGNORECASE),
    re.compile(r"\((Value Plus|Greatest Hits|Platinum)[^)]*\)", re.IGNORECASE),
]


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
    rev_match = REVISION_PATTERN.search(filename)
    if rev_match:
        version_info.append(rev_match.group(0).strip("()"))

    # Check for special editions
    for pattern in VERSION_EDITION_PATTERNS:
        match = pattern.search(filename)
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
        if DISC_PATTERN.search(filename):
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
        if any(pattern.search(filename) for pattern in patterns):
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
    disc_match = DISC_PATTERN.search(base)
    if disc_match:
        disc_info = disc_match.group(0)
        # Remove the disc info from base temporarily to avoid duplication
        base = base.replace(disc_match.group(0), "")

    # Remove region tags specifically (not all parentheses)
    for patterns in REGION_PATTERNS.values():
        for pattern in patterns:
            base = pattern.sub("", base)

    # Remove other common tags but preserve disc info
    # Remove revision info
    base = REVISION_PATTERN.sub("", base)
    # Remove version patterns like "Version 3" or "v2.0"
    base = VERSION_PATTERN.sub("", base)
    base = VDOT_PATTERN.sub("", base)
    # Remove quality indicators
    base = QUALITY_PATTERN.sub("", base)
    # Remove other edition info
    base = EDITION_PATTERN.sub("", base)
    # Remove trailing numbers like "- 1" or " - 1"
    base = TRAILING_NUMBER_PATTERN.sub("", base)

    # Clean up extra whitespace
    base = WHITESPACE_PATTERN.sub(" ", base).strip()

    # Add disc info back if it existed
    if disc_info:
        base += " " + disc_info.strip()

    return base
