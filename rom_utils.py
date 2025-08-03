import os
import re

# Region patterns - matches common ROM naming conventions
REGION_PATTERNS = {
    'japan': [r'\(J\)', r'\(Japan\)', r'\(JP\)', r'\(JPN\)', r'\[J\]', r'\[Japan\]'],
    'usa': [r'\(U\)', r'\(USA\)', r'\(US\)', r'\[U\]', r'\[USA\]', r'\[US\]'],
    'europe': [r'\(E\)', r'\(Europe\)', r'\(EUR\)', r'\[E\]', r'\[Europe\]'],
    'world': [r'\(W\)', r'\(World\)', r'\[W\]', r'\[World\]']
}


def get_region(filename):
    """Extract region from filename based on common ROM naming patterns."""

    for region, patterns in REGION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return region
    return 'unknown'

def get_base_name(filename):
    """
    Extract the base game name by removing region tags, revision info, etc.
    """
    # Remove file extension
    base = os.path.splitext(filename)[0]

    # Remove common ROM tags in parentheses and brackets
    base = re.sub(r'\s*[\(\[][^)\]]*[\)\]]', '', base)

    # Remove common revision/version patterns
    base = re.sub(r'\s*(Rev|v|Ver|Version)\s*\d+.*$', '', base, flags=re.IGNORECASE)
    base = re.sub(r'\s*-\s*\d+$', '', base)  # Remove trailing numbers like "- 1"

    # Clean up extra whitespace
    base = re.sub(r'\s+', ' ', base).strip()

    return base
