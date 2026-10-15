import pytest
from unittest.mock import patch, MagicMock
import requests
from api_client import fetch_live_game_feed, extract_game_context, MLBAPIError

@patch("api_client.requests.get")
def test_fetch_live_game_feed_success(mock_get):
    """Test successful live feed retrieval from MLB API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"gamePk": 12345, "liveData": {}}
    mock_get.return_value = mock_response

    data = fetch_live_game_feed(12345)
    assert data["gamePk"] == 12345
    mock_get.assert_called_once_with("https://statsapi.mlb.com/api/v1/game/12345/feed/live", timeout=10)

@patch("api_client.requests.get")
def test_fetch_live_game_feed_error(mock_get):
    """Test that MLBAPIError is raised on network or HTTP failure."""
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")

    with pytest.raises(MLBAPIError):
        fetch_live_game_feed(99999)

def test_extract_game_context_normal():
    """Test proper normalization of game linescore and situational metrics."""
    sample_feed = {
        "liveData": {
            "linescore": {
                "currentInning": 5,
                "outs": 2,
                "offense": {
                    "first": {"id": 1},
                    "second": None,
                    "third": {"id": 2}
                }
            }
        }
    }

    context = extract_game_context(sample_feed)
    assert context["inning"] == 5
    assert context["outs"] == 2
    assert context["runners_count"] == 2  # First and third occupied
    assert context["pitch_count"] == 0   # Default fallback