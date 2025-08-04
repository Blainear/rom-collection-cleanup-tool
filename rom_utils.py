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
    'japan': [r'\(J\)', r'\(Japan\)', r'\(JP\)', r'\(JPN\)', r'\[J\]', r'\[Japan\]'],
    'usa': [r'\(U\)', r'\(USA\)', r'\(US\)', r'\[U\]', r'\[USA\]', r'\[US\]'],
    'europe': [r'\(E\)', r'\(Europe\)', r'\(EUR\)', r'\[E\]', r'\[Europe\]'],
    'world': [r'\(W\)', r'\(World\)', r'\[W\]', r'\[World\]']
}


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
        return 'unknown'
    
    for region, patterns in REGION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return region
    return 'unknown'

def get_base_name(filename: str) -> str:
    """
    Extract the base game name by removing region tags, revision info, etc.
    
    Args:
        filename: The ROM filename to parse
        
    Returns:
        The cleaned base name of the game
        
    Examples:
        >>> get_base_name("Super Mario Bros. (USA).nes")
        'Super Mario Bros.'
        >>> get_base_name("Final Fantasy (J) (Rev 2).snes")
        'Final Fantasy'
        >>> get_base_name("Sonic - 1 (Europe) [!].zip")
        'Sonic'
    """
    if not filename or not isinstance(filename, str):
        return ""
    
    # Remove file extension
    base = os.path.splitext(filename)[0]

    # Remove common ROM tags in parentheses and brackets
    base = re.sub(r'\s*[\(\[][^)\]]*[\)\]]', '', base)

    # Remove common revision/version patterns
    base = re.sub(r'\s*(Rev|v|Ver|Version)\s*\d+.*$', '', base, flags=re.IGNORECASE)
    base = re.sub(r'\s*-\s*\d+$', '', base)  # Remove trailing numbers like "- 1"

    # Clean up extra whitespace and return
    base = re.sub(r'\s+', ' ', base).strip()

    return base
