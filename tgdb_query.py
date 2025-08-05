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

# Rate limiting globals
_last_request_time = 0
_request_count = 0
_hour_start = 0
_requests_this_hour = 0

# Rate limiting constants
MIN_REQUEST_INTERVAL = 1.5  # 1.5 seconds between requests (conservative)
MAX_REQUESTS_PER_HOUR = 500  # Conservative limit for shared public key


def _enforce_rate_limit():
    """Enforce rate limiting to avoid 403 errors."""
    global _last_request_time, _requests_this_hour, _hour_start

    current_time = time.time()

    # Reset hourly counter if needed
    if current_time - _hour_start > 3600:  # 1 hour
        _hour_start = current_time
        _requests_this_hour = 0

    # Check if we've hit hourly limit
    if _requests_this_hour >= MAX_REQUESTS_PER_HOUR:
        wait_time = 3600 - (current_time - _hour_start)
        if wait_time > 0:
            print(f"API hourly limit reached. Waiting {wait_time:.0f} seconds...")
            time.sleep(wait_time)
            _hour_start = time.time()
            _requests_this_hour = 0

    # Enforce minimum interval between requests
    time_since_last = current_time - _last_request_time
    if time_since_last < MIN_REQUEST_INTERVAL:
        sleep_time = MIN_REQUEST_INTERVAL - time_since_last
        time.sleep(sleep_time)

    _last_request_time = time.time()
    _requests_this_hour += 1


def _generate_search_terms(game_name):
    """Generate progressive search terms for better database matching."""
    import re

    terms = []
    clean_name = game_name.strip()

    # 1. Original cleaned name
    terms.append(clean_name)

    # 2. Remove common parenthetical info (language, region, etc.)
    no_parens = re.sub(r"\s*\([^)]*\)", "", clean_name).strip()
    if no_parens and no_parens != clean_name:
        terms.append(no_parens)

    # 3. Remove subtitle (everything after " - ")
    no_subtitle = re.sub(r"\s*-\s*.*$", "", no_parens).strip()
    if no_subtitle and no_subtitle != no_parens:
        terms.append(no_subtitle)

    # 4. Remove version/disc numbers
    no_numbers = re.sub(
        r"\s*(Disc|CD|Disk)\s*\d+.*$", "", no_subtitle, flags=re.IGNORECASE
    ).strip()
    if no_numbers and no_numbers != no_subtitle:
        terms.append(no_numbers)

    # 5. Remove common prefixes/suffixes
    final_clean = re.sub(
        r"\s*(The|A|An)\s+", "", no_numbers, flags=re.IGNORECASE
    ).strip()
    if final_clean and final_clean != no_numbers:
        terms.append(final_clean)

    # Remove duplicates while preserving order
    unique_terms = []
    for term in terms:
        if term and term not in unique_terms:
            unique_terms.append(term)

    return unique_terms


def query_tgdb_game(game_name, file_extension=None, tgdb_api_key=None, logger=None):
    """Query TheGamesDB for game information and alternative names."""

    def log(message):
        if logger:
            logger(message)
        else:
            print(message)

    if not requests:
        log("ERROR: requests library not available - TheGamesDB integration disabled")
        return None

    if not tgdb_api_key:
        log("ERROR: TGDB_API_KEY not provided - API integration disabled")
        return None

    cache_key = hashlib.md5(
        f"{game_name}_{file_extension or 'unknown'}".encode()
    ).hexdigest()

    if cache_key in GAME_CACHE:
        log(f"Cache hit for: {game_name}")
        return GAME_CACHE[cache_key]

    # Generate progressive search terms for better matching
    search_terms = _generate_search_terms(game_name)
    log(f"Trying search terms: {search_terms}")

    # Try each search term until we find a good match
    for term_index, search_term in enumerate(search_terms):
        best_match = _try_search_term(
            search_term, tgdb_api_key, game_name, term_index, logger
        )
        if best_match:
            GAME_CACHE[cache_key] = best_match
            return best_match

    log(f"All search terms failed for: {game_name}")
    GAME_CACHE[cache_key] = None
    return None


def _try_search_term(search_term, tgdb_api_key, original_name, term_index, logger=None):
    """Try a single search term against TheGamesDB API."""

    def log(message):
        if logger:
            logger(message)
        else:
            print(message)

    backoff = 0.5

    for attempt in range(3):
        try:
            # Enforce rate limiting before making API request
            _enforce_rate_limit()

            # Use TheGamesDB API to search for games by name
            url = "https://api.thegamesdb.net/v1/Games/ByGameName"
            params = {
                "apikey": tgdb_api_key,
                "name": search_term,
                "fields": "games",
                "include": "boxart",
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 429:
                # Rate limit exceeded - wait longer
                wait_time = backoff * (2**attempt)  # Exponential backoff
                log(f"Rate limit hit (429), waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                continue

            if response.status_code == 403:
                # Forbidden - likely hit usage limits
                wait_time = 30 * (attempt + 1)  # Wait 30, 60, 90 seconds
                log(f"API access forbidden (403), waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            data = response.json()

            if not data.get("data") or not data["data"].get("games"):
                if term_index == 0:  # Only log for first attempt
                    log(f"TheGamesDB API returned no results for: {search_term}")
                return None

            games = data["data"]["games"]
            if term_index == 0:  # Only log for first attempt
                log(f"TheGamesDB API returned {len(games)} results for: {search_term}")

            scored_matches = []

            for game in games:
                game_title = game.get("game_title", "")

                # Compare against both original name and search term
                ratio_original = SequenceMatcher(
                    None, original_name.lower(), game_title.lower()
                ).ratio()
                ratio_search = SequenceMatcher(
                    None, search_term.lower(), game_title.lower()
                ).ratio()

                # Use the better of the two ratios
                ratio = max(ratio_original, ratio_search)

                # More lenient threshold since TGDB is ROM-focused
                # Lower threshold for later search terms since they're more generic
                threshold = (
                    0.6 if term_index == 0 else max(0.5, 0.8 - (term_index * 0.1))
                )

                if ratio >= threshold:
                    scored_matches.append(
                        {
                            "score": ratio,
                            "canonical_name": game_title,
                            "matched_on": game_title,
                            "match_type": "main",
                            "platform_bonus": 0,
                            "all_names": [game_title],
                            "game_id": game.get("id"),
                            "platform": game.get("platform"),
                            "search_term_used": search_term,
                            "term_index": term_index,
                        }
                    )

            if scored_matches:
                # Sort by score and return the best match
                scored_matches.sort(key=lambda x: x["score"], reverse=True)
                best = scored_matches[0]

                log(
                    f"Best match for '{original_name}': '{best['canonical_name']}' "
                    f"(score: {best['score']:.3f}, search term: '{search_term}')"
                )

                return best

            if term_index == 0:  # Only log for first attempt
                log(f"No suitable matches found for: {search_term}")
            return None

        except requests.exceptions.RequestException as e:
            if term_index == 0:  # Only log for first attempt
                log(f"Request error on attempt {attempt + 1}: {e}")
            if attempt < 2:  # Only sleep if we're going to retry
                time.sleep(backoff * (attempt + 1))
        except Exception as e:
            if term_index == 0:  # Only log for first attempt
                log(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt < 2:  # Only sleep if we're going to retry
                time.sleep(backoff * (attempt + 1))

    # All attempts failed for this search term
    if term_index == 0:  # Only log for first attempt
        log(f"All API attempts failed for search term: {search_term}")
    return None


def get_canonical_name(game_name, file_extension=None, tgdb_api_key=None, logger=None):
    """Get canonical name using TheGamesDB or fallback to cache/simple matching."""

    def log(message):
        if logger:
            logger(message)
        else:
            print(message)

    log(f"Looking up canonical name for: {game_name} ({file_extension})")

    # Try TheGamesDB first
    tgdb_result = query_tgdb_game(game_name, file_extension, tgdb_api_key, logger)
    if tgdb_result:
        # Use the actual matched name, not the canonical TGDB name
        canonical = tgdb_result["matched_on"]  # This is the name that actually matched
        if canonical != game_name:
            log(f"Canonical name: '{game_name}' -> '{canonical}'")
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
        log(
            f"Fallback canonical name: '{game_name}' -> '{canonical}' (ratio: {best_ratio:.3f})"
        )
        return canonical

    # No matches found, return original name
    return game_name
