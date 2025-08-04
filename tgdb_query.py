"""
TheGamesDB query function for ROM cleanup tool.
Replaces IGDB functionality.
"""

import hashlib
import time
from difflib import SequenceMatcher

try:
    import requests
except ImportError:
    requests = None

# Global cache for game queries
GAME_CACHE = {}

def query_tgdb_game(game_name, file_extension=None, tgdb_api_key=None):
    """Query TheGamesDB for game information and alternative names."""
    if not requests:
        print("ERROR: requests library not available - TheGamesDB integration disabled")
        return None

    if not tgdb_api_key:
        print("ERROR: TGDB_API_KEY not provided - API integration disabled")
        return None

    cache_key = hashlib.md5(
        f"{game_name}_{file_extension or 'unknown'}".encode()
    ).hexdigest()

    if cache_key in GAME_CACHE:
        print(f"Cache hit for: {game_name}")
        return GAME_CACHE[cache_key]

    # Clean the game name for better matching
    clean_name = game_name.strip()
    
    backoff = 0.5
    for attempt in range(3):
        try:
            # Use TheGamesDB API to search for games by name
            url = f"https://api.thegamesdb.net/v1/Games/ByGameName"
            params = {
                'apikey': tgdb_api_key,
                'name': clean_name,
                'fields': 'games',
                'include': 'boxart'
            }
            
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 429:
                time.sleep(backoff * (attempt + 1))
                continue

            response.raise_for_status()
            data = response.json()
            
            if not data.get('data') or not data['data'].get('games'):
                print(f"TheGamesDB API returned no results for: {game_name}")
                GAME_CACHE[cache_key] = None
                return None

            games = data['data']['games']
            print(f"TheGamesDB API returned {len(games)} results for: {game_name}")

            scored_matches = []

            for game in games:
                game_title = game.get('game_title', '')
                
                # For now, we'll use a simple matching approach
                # TheGamesDB doesn't have as detailed alternative names as IGDB
                ratio = SequenceMatcher(None, game_name.lower(), game_title.lower()).ratio()
                
                # More lenient threshold since TGDB is ROM-focused
                if ratio >= 0.6:
                    scored_matches.append({
                        "score": ratio,
                        "canonical_name": game_title,
                        "matched_on": game_title,
                        "match_type": "main",
                        "platform_bonus": 0,
                        "all_names": [game_title],
                        "game_id": game.get('id'),
                        "platform": game.get('platform')
                    })

            if scored_matches:
                # Sort by score and return the best match
                scored_matches.sort(key=lambda x: x["score"], reverse=True)
                best = scored_matches[0]

                print(
                    f"Best match for '{game_name}': '{best['canonical_name']}' "
                    f"(score: {best['score']:.3f})"
                )

                GAME_CACHE[cache_key] = best
                return best

            print(f"No suitable matches found for: {game_name}")

        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {e}")
            if attempt < 2:  # Only sleep if we're going to retry
                time.sleep(backoff * (attempt + 1))
        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt < 2:  # Only sleep if we're going to retry
                time.sleep(backoff * (attempt + 1))

        # If we reach here, the request failed
        if attempt == 2:  # Last attempt failed
            print(f"All API attempts failed for: {game_name}")
            # Rate limiting - be respectful to TheGamesDB
            time.sleep(0.5)

    GAME_CACHE[cache_key] = None
    return None


def get_canonical_name(game_name, file_extension=None, tgdb_api_key=None):
    """Get canonical name using TheGamesDB or fallback to cache/simple matching."""
    print(f"Looking up canonical name for: {game_name} ({file_extension})")

    # Try TheGamesDB first
    tgdb_result = query_tgdb_game(game_name, file_extension, tgdb_api_key)
    if tgdb_result:
        # Use the actual matched name, not the canonical TGDB name
        canonical = tgdb_result["matched_on"]  # This is the name that actually matched
        if canonical != game_name:
            print(f"Canonical name: '{game_name}' -> '{canonical}'")
        return canonical

    # Fallback: check for obvious matches in already cached games
    best_match = None
    best_ratio = 0.0

    for cached_key, cached_result in GAME_CACHE.items():
        if not cached_result:
            continue
            
        if file_extension and not cached_key.endswith(file_extension or "unknown"):
            continue

        cached_name = cached_result.get("canonical_name", "")
        ratio = SequenceMatcher(None, game_name.lower(), cached_name.lower()).ratio()

        if ratio > best_ratio and ratio > 0.8:  # High threshold for fallback
            best_ratio = ratio
            best_match = cached_result

    if best_match:
        canonical = best_match["canonical_name"]
        print(f"Fallback canonical name: '{game_name}' -> '{canonical}' (ratio: {best_ratio:.3f})")
        return canonical

    # No matches found, return original name
    return game_name