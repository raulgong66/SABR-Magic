import requests
from typing import Dict, Any, Optional

class MLBApiClient:
    """
    Client for interacting with the public MLB Stats API (statsapi.mlb.com).
    Fetches real-time play-by-play data and game schedules.
    """
    BASE_URL = "https://statsapi.mlb.com/api/v1"

    def get_todays_games(self) -> list:
        """
        Fetches today's schedule to obtain active gamePk IDs.
        """
        url = f"{self.BASE_URL}/schedule?sportId=1"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('dates'):
                return data['dates'][0].get('games', [])
            return []
        except requests.RequestException as e:
            print(f"Error fetching schedule: {e}")
            return []

    def get_play_by_play(self, game_pk: int) -> Optional[Dict[str, Any]]:
        """
        Fetches real-time play-by-play data for a specific game.
        """
        url = f"{self.BASE_URL}/game/{game_pk}/playByPlay"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching play-by-play for game {game_pk}: {e}")
            return None
