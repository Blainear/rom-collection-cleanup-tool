"""
Local database of cross-regional game name mappings.
This provides enhanced matching without requiring external APIs.
"""

# Common cross-regional game name mappings
CROSS_REGIONAL_MAPPINGS = {
    # Capcom titles
    "biohazard": "resident evil",
    "biohazard 2": "resident evil 2", 
    "biohazard 3": "resident evil 3",
    "rockman": "mega man",
    "rockman x": "mega man x",
    "rockman 2": "mega man 2",
    "rockman 3": "mega man 3",
    "rockman 4": "mega man 4",
    "rockman 5": "mega man 5",
    "rockman 6": "mega man 6",
    "street fighter zero": "street fighter alpha",
    "street fighter zero 2": "street fighter alpha 2",
    "street fighter zero 3": "street fighter alpha 3",
    
    # Square/Enix titles
    "final fantasy ii": "final fantasy iv",  # JP FF2 = US FF4
    "final fantasy iii": "final fantasy vi", # JP FF3 = US FF6
    "seiken densetsu": "final fantasy adventure",
    "seiken densetsu 2": "secret of mana",
    "seiken densetsu 3": "trials of mana",
    "chrono trigger": "chrono trigger",  # Same name but different regions
    "dragon quest": "dragon warrior",
    "dragon quest ii": "dragon warrior ii",
    "dragon quest iii": "dragon warrior iii",
    "dragon quest iv": "dragon warrior iv",
    
    # Nintendo titles
    "super mario bros. 2": "super mario usa",  # JP version different
    "mario no super picross": "mario's super picross",
    "zelda no densetsu": "the legend of zelda",
    "fire emblem": "fire emblem",  # Many JP-only entries
    
    # Konami titles
    "akumajou dracula": "castlevania",
    "akumajou dracula x": "castlevania dracula x",
    "contra": "probotector",  # EU name
    "gradius": "nemesis",     # EU name
    
    # Other notable mappings
    "puyo puyo": "puyo pop",
    "bomberman": "dyna blaster",  # EU name
    "tetris": "tetris",  # Universal
    "pac-man": "puck man",  # Original JP name
    
    # Fighting games
    "tekken": "tekken",
    "virtua fighter": "virtua fighter",
    "king of fighters": "king of fighters",
    
    # RPGs
    "tales of phantasia": "tales of phantasia",
    "phantasy star": "phantasy star",
    "shin megami tensei": "revelations persona",  # Some entries
    
    # Sports games
    "winning eleven": "pro evolution soccer",
    "jikkyou powerful pro yakyuu": "power pros",
}

def get_canonical_mapping(game_name: str) -> str:
    """
    Get the canonical version of a game name using local mappings.
    
    Args:
        game_name: The game name to look up
        
    Returns:
        The canonical name if found, otherwise the original name
    """
    if not game_name:
        return game_name
        
    name_lower = game_name.lower().strip()
    
    # Direct mapping
    if name_lower in CROSS_REGIONAL_MAPPINGS:
        return CROSS_REGIONAL_MAPPINGS[name_lower]
    
    # Check if this is a mapped canonical name (reverse lookup)
    for jp_name, us_name in CROSS_REGIONAL_MAPPINGS.items():
        if name_lower == us_name.lower():
            return us_name  # Already canonical
    
    # Try partial matching for series
    for jp_name, us_name in CROSS_REGIONAL_MAPPINGS.items():
        if jp_name in name_lower:
            # Replace the Japanese part with US equivalent
            return game_name.lower().replace(jp_name, us_name).title()
    
    return game_name

def are_games_equivalent(game1: str, game2: str) -> bool:
    """
    Check if two game names represent the same game across regions.
    
    Args:
        game1: First game name
        game2: Second game name
        
    Returns:
        True if the games are equivalent across regions
    """
    if not game1 or not game2:
        return False
        
    # Normalize both names
    canonical1 = get_canonical_mapping(game1).lower().strip()
    canonical2 = get_canonical_mapping(game2).lower().strip()
    
    # Direct match
    if canonical1 == canonical2:
        return True
    
    # Check if they map to the same canonical name
    mapped1 = get_canonical_mapping(canonical1)
    mapped2 = get_canonical_mapping(canonical2)
    
    return mapped1.lower() == mapped2.lower()

def expand_game_mappings():
    """
    Expand the mappings to include reverse mappings automatically.
    This ensures bidirectional lookup works properly.
    """
    expanded = dict(CROSS_REGIONAL_MAPPINGS)
    
    # Add reverse mappings
    for jp_name, us_name in CROSS_REGIONAL_MAPPINGS.items():
        expanded[us_name.lower()] = us_name  # Canonical points to itself
        
    return expanded

# Initialize expanded mappings
EXPANDED_MAPPINGS = expand_game_mappings()