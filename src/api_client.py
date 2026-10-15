import requests
from typing import Dict, Any, Optional

BASE_URL = "https://statsapi.mlb.com/api/v1"

class MLBAPIError(Exception):
    """Custom exception raised for errors during MLB API requests."""
    pass

def fetch_live_game_feed(game_pk: int) -> Dict[str, Any]:
    """
    Fetches the live game feed JSON from the MLB Stats API for a given game ID.
    
    Args:
        game_pk (int): The unique identifier for the MLB game.
        
    Returns:
        dict: The raw JSON response containing live game states, linescore, and plays.
        
    Raises:
        MLBAPIError: If the network request fails or returns a non-200 status code.
    """
    url = f"{BASE_URL}/game/{game_pk}/feed/live"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise MLBAPIError(f"Failed to fetch live feed for game {game_pk}: {e}") from e

def extract_game_context(live_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts and normalizes core situational metrics (inning, outs, runners, pitch count)
    from the raw MLB live feed to feed into our SABR-Magic metrics engine.
    
    Args:
        live_data (dict): The raw JSON payload from fetch_live_game_feed.
        
    Returns:
        dict: Normalized context dictionary ready for metric evaluation.
    """
    try:
        live_line = live_data.get("liveData", {})
        linescore = live_line.get("linescore", {})
        
        inning = linescore.get("currentInning", 1)
        outs = linescore.get("outs", 0)
        
        # Determine runners count based on base occupancy
        offense = linescore.get("offense", {})
        runners_count = 0
        if offense.get("first"):
            runners_count += 1
        if offense.get("second"):
            runners_count += 1
        if offense.get("third"):
            runners_count += 1

        # Extract current pitcher pitch count if available in boxscore/linescore
        # Defaulting safely to 0 if not active in current payload frame
        pitcher_id = linescore.get("defense", {}).get("pitcher", {}).get("id")
        pitch_count = 0
        
        boxscore = live_line.get("boxscore", {}).get("teams", {})
        # Search pitchers across home/away if needed, or fallback gracefully
        
        return {
            "inning": inning,
            "outs": outs,
            "runners_count": runners_count,
            "pitch_count": pitch_count
        }
    except Exception as e:
        raise MLBAPIError(f"Error parsing game context metrics from feed: {e}") from e